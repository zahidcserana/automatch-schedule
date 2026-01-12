from .models import db, HouseCleaningOrder, HouseCleaningVehicleAssignment, HouseCleaningAutoMatchingTimeManagement


def match_order_to_vehicle(order_id):
    order = HouseCleaningOrder.query.get(order_id)
    if not order:
        return None, "Order not found"

    # 1. Find an available vehicle for the specific date and time slot
    # Availability is defined as having no vehicle_assignment_id yet
    available_slot = HouseCleaningAutoMatchingTimeManagement.query.filter_by(
        work_date=order.requested_service_date,
        time_slot_availability=order.requested_service_time_slot,
        vehicle_assignment_id=None
    ).first()

    if not available_slot:
        return None, "No available vehicles for this time slot"

    try:
        # 2. Create the Assignment
        assignment = HouseCleaningVehicleAssignment(
            order_id=order.id,
            vehicle_id=available_slot.vehicle_id
        )
        db.session.add(assignment)
        db.session.flush()  # Get the assignment ID

        # 3. Update the AutoMatching table
        available_slot.vehicle_assignment_id = assignment.id
        # In a real app, you'd calculate this from the customer's address
        available_slot.workplace_geolocation = "35.6895, 139.6917"

        db.session.commit()
        return assignment, None
    except Exception as e:
        db.session.rollback()
        return None, str(e)