from decimal import Decimal
from http import HTTPStatus
from typing import Any, Dict

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, url_for

from src.models.currency import Currency
from src.models.money import Money
from src.models.plan import Plan, PlanTier

web_bp = Blueprint("web", __name__, template_folder="templates")


@web_bp.route("/", methods=["GET"])
def index():
    """Strona główna - Dashboard z katalogiem planów i symulatorem rozliczeń."""
    service = current_app.config["BILLING_SERVICE"]
    plans = current_app.config["PLANS_CATALOG"]
    subscriptions = service.list_subscriptions()

    return render_template(
        "dashboard.html",
        plans=plans,
        subscriptions=subscriptions,
    )


@web_bp.route("/subscriptions", methods=["POST"])
def create_subscription():
    """Tworzy nową subskrypcję na podstawie formularza."""
    service = current_app.config["BILLING_SERVICE"]
    plans = current_app.config["PLANS_CATALOG"]

    customer_id = request.form.get("customer_id", "").strip()
    plan_tier_str = request.form.get("plan_tier", "").strip()

    if not customer_id or not plan_tier_str:
        return jsonify({"error": "Brakujące wymagane pola customer_id lub plan_tier"}), HTTPStatus.BAD_REQUEST

    try:
        tier = PlanTier(plan_tier_str)
    except ValueError:
        return jsonify({"error": f"Nieprawidłowy poziom planu: {plan_tier_str}"}), HTTPStatus.BAD_REQUEST

    plan = plans.get(tier)
    if not plan:
        return jsonify({"error": "Plan nie został odnaleziony w katalogu"}), HTTPStatus.NOT_FOUND

    subscription_id = f"sub-{len(service.list_subscriptions()) + 1:03d}"
    service.create_subscription(
        subscription_id=subscription_id,
        customer_id=customer_id,
        plan=plan,
        activate=True,
    )

    return redirect(url_for("web.index"))


@web_bp.route("/subscriptions/<subscription_id>/migrate", methods=["POST"])
def migrate_subscription(subscription_id: str):
    """Przeprowadza migrację planu ze statusem proration."""
    service = current_app.config["BILLING_SERVICE"]
    plans = current_app.config["PLANS_CATALOG"]

    target_tier_str = request.form.get("target_tier", "").strip()
    current_day_raw = request.form.get("current_day", "15").strip()

    try:
        target_tier = PlanTier(target_tier_str)
        current_day = int(current_day_raw)
    except (ValueError, TypeError):
        return jsonify({"error": "Nieprawidłowy plan docelowy lub dzień cyklu"}), HTTPStatus.BAD_REQUEST

    new_plan = plans.get(target_tier)
    if not new_plan:
        return jsonify({"error": "Plan docelowy nie istnieje"}), HTTPStatus.NOT_FOUND

    try:
        service.migrate_plan(
            subscription_id=subscription_id,
            new_plan=new_plan,
            current_day=current_day,
        )
    except KeyError:
        return jsonify({"error": f"Subskrypcja {subscription_id} nie istnieje"}), HTTPStatus.NOT_FOUND
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTPStatus.UNPROCESSABLE_ENTITY

    return redirect(url_for("web.index"))


@web_bp.route("/subscriptions/<subscription_id>/cancel", methods=["POST"])
def cancel_subscription(subscription_id: str):
    """Anuluje wybraną subskrypcję."""
    service = current_app.config["BILLING_SERVICE"]
    try:
        service.cancel_subscription(subscription_id)
    except KeyError:
        return jsonify({"error": f"Subskrypcja {subscription_id} nie istnieje"}), HTTPStatus.NOT_FOUND

    return redirect(url_for("web.index"))


@web_bp.route("/subscriptions/<subscription_id>/invoice", methods=["GET"])
def view_invoice(subscription_id: str):
    """Podgląd wizualnej faktury za dany okres."""
    service = current_app.config["BILLING_SERVICE"]
    sub = service.get_subscription(subscription_id)
    if not sub:
        return jsonify({"error": "Subskrypcja nie istnieje"}), HTTPStatus.NOT_FOUND

    total_bill = service.calculate_monthly_bill(subscription_id)

    return render_template(
        "invoice.html",
        subscription=sub,
        total_bill=total_bill,
    )


@web_bp.route("/api/plans", methods=["GET"])
def get_plans():
    """Zwraca listę dostępnych planów w formacie JSON."""
    plans = current_app.config["PLANS_CATALOG"]
    payload = [
        {
            "tier": plan.tier.value,
            "name": plan.name,
            "base_price": str(plan.base_price.amount),
            "currency": plan.base_price.currency.value,
            "included_requests": plan.included_requests,
            "description": plan.description,
        }
        for plan in plans.values()
    ]
    return jsonify(payload), HTTPStatus.OK


@web_bp.route("/api/proration/calculate", methods=["POST"])
def calculate_proration_api():
    """Kalkulator REST API dla symulatora interfejsu (AJAX / fetch)."""
    data: Dict[str, Any] = request.get_json(silent=True) or {}

    plans = current_app.config["PLANS_CATALOG"]
    engine = current_app.config["PRORATION_ENGINE"]

    from_tier_str = data.get("from_tier")
    to_tier_str = data.get("to_tier")
    current_day = data.get("current_day", 15)
    total_cycle_days = data.get("total_cycle_days", 30)

    try:
        from_plan = plans[PlanTier(from_tier_str)]
        to_plan = plans[PlanTier(to_tier_str)]
        current_day = int(current_day)
        total_cycle_days = int(total_cycle_days)
    except (KeyError, ValueError, TypeError):
        return jsonify({"error": "Nieprawidłowe parametry kalkulacji"}), HTTPStatus.BAD_REQUEST

    try:
        result = engine.calculate_migration(
            current_price=from_plan.base_price,
            new_price=to_plan.base_price,
            current_day=current_day,
            total_cycle_days=total_cycle_days,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), HTTPStatus.UNPROCESSABLE_ENTITY

    return jsonify({
        "unused_credit": str(result.unused_credit.amount),
        "new_plan_charge": str(result.new_plan_charge.amount),
        "net_amount_due": str(result.net_amount_due.amount),
        "credit_balance": str(result.credit_balance.amount),
        "remaining_days": result.remaining_days,
        "total_cycle_days": result.total_cycle_days,
        "currency": result.unused_credit.currency.value,
    }), HTTPStatus.OK
