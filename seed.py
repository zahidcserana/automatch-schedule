from datetime import date, time

from app import create_app, db
from app.models import (
    HouseCleaningPartner,
    HouseCleaningPartnerVehicle,
    HouseCleaningPartnerStaff,
    HouseCleaningVehicleWorkSchedule
)

app = create_app()


def seed_data():
    with app.app_context():
        # 1. Clean existing data (Optional - be careful!)
        db.drop_all()
        db.create_all()
        print("Database tables recreated.")

        # 2. Create a Partner
        partner = HouseCleaningPartner(name="Sparkle Clean Co.")
        db.session.add(partner)
        db.session.flush()  # Flush to get the ID

        # 3. Create a Vehicle
        vehicle = HouseCleaningPartnerVehicle(
            name="Van-01 (Tokyo Central)",
            partner_id=partner.id,
            status=1
        )
        db.session.add(vehicle)

        # 4. Create Staff Members
        staff1 = HouseCleaningPartnerStaff(
            name="Tanaka Taro",
            name_kana="タナカ タロウ",
            gender=1  # Male
        )
        staff2 = HouseCleaningPartnerStaff(
            name="Sato Hanako",
            name_kana="サトウ ハナコ",
            gender=2  # Female
        )
        db.session.add_all([staff1, staff2])

        # 5. Create an initial Work Schedule
        schedule = HouseCleaningVehicleWorkSchedule(
            vehicle_id=1,
            work_date=date(2026, 1, 10),
            work_start_at=time(9, 0),
            work_end_at=time(17, 0)
        )
        db.session.add(schedule)

        db.session.commit()
        print("Database seeded successfully!")


if __name__ == '__main__':
    seed_data()
