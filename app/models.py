from sqlalchemy import and_

from . import db


class HouseCleaningPartner(db.Model):
    __tablename__ = 'house_cleaning_partners'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    vehicles = db.relationship('HouseCleaningPartnerVehicle', backref='partner')


class HouseCleaningPartnerVehicle(db.Model):
    __tablename__ = 'house_cleaning_partner_vehicles'
    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('house_cleaning_partners.id'))
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Integer, default=1)

    schedules = db.relationship('HouseCleaningVehicleWorkSchedule', backref='vehicle', cascade="all, delete-orphan")


class HouseCleaningVehicleWorkSchedule(db.Model):
    __tablename__ = 'house_cleaning_vehicle_work_schedules'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('house_cleaning_partner_vehicles.id'), nullable=False)
    work_date = db.Column(db.Date, nullable=False)
    work_start_at = db.Column(db.Time, nullable=False)
    work_end_at = db.Column(db.Time, nullable=False)

    def check_overlap(self):
        overlap = HouseCleaningVehicleWorkSchedule.query.filter(
            HouseCleaningVehicleWorkSchedule.vehicle_id == self.vehicle_id,
            HouseCleaningVehicleWorkSchedule.work_date == self.work_date,
            HouseCleaningVehicleWorkSchedule.id != self.id,
            and_(
                HouseCleaningVehicleWorkSchedule.work_start_at < self.work_end_at,
                HouseCleaningVehicleWorkSchedule.work_end_at > self.work_start_at
            )
        ).first()
        return overlap


class HouseCleaningOrder(db.Model):
    __tablename__ = 'house_cleaning_orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    requested_service_date = db.Column(db.Date, nullable=False)
    requested_service_time_slot = db.Column(db.Integer, nullable=False)


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    orders = db.relationship('HouseCleaningOrder', backref='customer', cascade="all, delete-orphan")


class HouseCleaningVehicleAssignment(db.Model):
    __tablename__ = 'house_cleaning_vehicle_assignments'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('house_cleaning_orders.id'))
    vehicle_id = db.Column(db.Integer, db.ForeignKey('house_cleaning_partner_vehicles.id'))


class HouseCleaningAutoMatchingTimeManagement(db.Model):
    __tablename__ = 'house_cleaning_auto_matching_time_management'
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('house_cleaning_partner_vehicles.id'))
    work_date = db.Column(db.Date, nullable=False)
    time_slot_availability = db.Column(db.Integer, nullable=False)
    vehicle_address_geolocation = db.Column(db.String(255), nullable=False)
    vehicle_work_schedule_id = db.Column(db.Integer, db.ForeignKey('house_cleaning_vehicle_work_schedules.id'))
    vehicle_assignment_id = db.Column(db.Integer, db.ForeignKey('house_cleaning_vehicle_assignments.id'), nullable=True)
    workplace_geolocation = db.Column(db.String(255), nullable=False)

    vehicle = db.relationship('HouseCleaningPartnerVehicle')
    assignment = db.relationship('HouseCleaningVehicleAssignment', backref='matching_record')
