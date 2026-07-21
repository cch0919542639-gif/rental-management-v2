from app.models.move_out_settlement import MoveOutSettlement
from app.models.parties import Contract, Property, Room
from app.repositories._helpers import session_get_or_404


class MoveOutSettlementRepository:
    @staticmethod
    def get_or_404(settlement_id: int):
        return session_get_or_404(MoveOutSettlement, settlement_id)

    @staticmethod
    def list_filtered(
        *,
        status: str | None = None,
        property_ids: list[int] | None = None,
        move_out_from=None,
        move_out_to=None,
    ):
        query = MoveOutSettlement.query.join(Contract).join(Room).join(Property)
        if status:
            query = query.filter_by(status=status)
        if property_ids is not None:
            query = query.filter(Property.id.in_(property_ids))
        if move_out_from:
            query = query.filter(MoveOutSettlement.move_out_date >= move_out_from)
        if move_out_to:
            query = query.filter(MoveOutSettlement.move_out_date <= move_out_to)
        return query.order_by(MoveOutSettlement.move_out_date.desc(), MoveOutSettlement.id.desc()).all()

    @staticmethod
    def find_for_contract(contract_id: int):
        return MoveOutSettlement.query.filter_by(contract_id=contract_id).first()
