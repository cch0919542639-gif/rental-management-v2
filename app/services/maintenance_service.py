from app.repositories import RoomRepository


class MaintenanceService:
    @staticmethod
    def room_snapshot():
        return [
            {
                "room_id": room.id,
                "property_name": room.property.name,
                "room_number": room.room_number,
                "status": room.status,
                "notes": room.notes,
            }
            for room in RoomRepository.list_all()
        ]
