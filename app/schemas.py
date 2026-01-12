from marshmallow import fields, validates_schema, ValidationError

from . import ma, db
from .models import HouseCleaningVehicleWorkSchedule, Customer, HouseCleaningOrder


class WorkScheduleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = HouseCleaningVehicleWorkSchedule
        load_instance = True
        include_fk = True

    @validates_schema
    def validate_times(self, data, **kwargs):
        if data['work_start_at'] >= data['work_end_at']:
            raise ValidationError("Start time must be before end time")


schedule_schema = WorkScheduleSchema()
schedules_schema = WorkScheduleSchema(many=True)


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True
        sqla_session = db.session


class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = HouseCleaningOrder
        load_instance = True
        include_fk = True  # Shows customer_id in JSON output
        sqla_session = db.session


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)
