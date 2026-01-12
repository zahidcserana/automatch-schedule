from flask import Blueprint, request, jsonify

from .models import HouseCleaningVehicleWorkSchedule, HouseCleaningAutoMatchingTimeManagement
from .models import db, Customer, HouseCleaningOrder
from .schemas import customer_schema, customers_schema, order_schema, orders_schema
from .services import match_order_to_vehicle

api = Blueprint('api', __name__)


@api.route('/schedules', methods=['POST'])
def create_schedule():
    from .schemas import schedule_schema
    data = request.get_json()
    try:
        new_schedule = schedule_schema.load(data, session=db.session)

        if new_schedule.check_overlap():
            return jsonify({"error": "Schedule overlap detected"}), 422

        db.session.add(new_schedule)
        db.session.commit()
        generate_availability_slots(new_schedule)
        return schedule_schema.dump(new_schedule), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@api.route('/schedules', methods=['GET'])
def list_schedules():
    from .schemas import schedules_schema
    schedules = HouseCleaningVehicleWorkSchedule.query.all()
    return jsonify(schedules_schema.dump(schedules)), 200


# --- CUSTOMER CRUD ---
@api.route('/customers', methods=['POST'])
def create_customer():
    data = request.get_json()
    new_customer = customer_schema.load(data, session=db.session)
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.dump(new_customer), 201


@api.route('/customers', methods=['GET'])
def get_customers():
    all_customers = Customer.query.all()
    return jsonify(customers_schema.dump(all_customers)), 200


# --- ORDER CRUD ---
@api.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    new_order = order_schema.load(data)
    db.session.add(new_order)
    db.session.commit()

    # Attempt immediate matching
    assignment, _ = match_order_to_vehicle(new_order.id)

    response = order_schema.dump(new_order)
    response['matched'] = True if assignment else False
    return jsonify(response), 201


@api.route('/orders_old', methods=['POST'])
def create_order_old():
    data = request.get_json()
    try:
        new_order = order_schema.load(data, session=db.session)
        db.session.add(new_order)
        db.session.commit()
        return order_schema.dump(new_order), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@api.route('/orders', methods=['GET'])
def get_orders():
    # Optional: filter by customer_id if provided in query params
    customer_id = request.args.get('customer_id')
    if customer_id:
        results = HouseCleaningOrder.query.filter_by(customer_id=customer_id).all()
    else:
        results = HouseCleaningOrder.query.all()
    return jsonify(orders_schema.dump(results)), 200


@api.route('/orders/<int:id>', methods=['PUT'])
def update_order(id):
    order = HouseCleaningOrder.query.get_or_404(id)
    data = request.get_json()
    updated_order = order_schema.load(data, instance=order, session=db.session, partial=True)
    db.session.commit()
    return order_schema.dump(updated_order), 200


@api.route('/orders/<int:id>', methods=['DELETE'])
def delete_order(id):
    order = HouseCleaningOrder.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return '', 204


@api.route('/orders/<int:order_id>/auto-match', methods=['POST'])
def auto_match_order(order_id):
    assignment, error = match_order_to_vehicle(order_id)

    if error:
        return jsonify({"status": "failed", "message": error}), 422

    return jsonify({
        "status": "success",
        "assignment_id": assignment.id,
        "vehicle_id": assignment.vehicle_id
    }), 200


# In routes.py after creating a HouseCleaningVehicleWorkSchedule
def generate_availability_slots(schedule):
    availability = HouseCleaningAutoMatchingTimeManagement(
        vehicle_id=schedule.vehicle_id,
        work_date=schedule.work_date,
        time_slot_availability=1,
        vehicle_address_geolocation="Initial Office Location",
        vehicle_work_schedule_id=schedule.id,
        workplace_geolocation=""  # Empty until matched
    )
    db.session.add(availability)
    db.session.commit()
