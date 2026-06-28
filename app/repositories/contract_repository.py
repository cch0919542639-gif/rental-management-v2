from app.models import Contract


class ContractRepository:
    @staticmethod
    def list_all():
        return Contract.query.order_by(Contract.start_date.desc()).all()

    @staticmethod
    def get_or_404(contract_id: int):
        return Contract.query.get_or_404(contract_id)

    @staticmethod
    def active_for_room(room_id: int):
        return Contract.query.filter_by(room_id=room_id, status="active").first()

    @staticmethod
    def list_active():
        return Contract.query.filter_by(status="active").all()
