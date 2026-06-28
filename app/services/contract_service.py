from datetime import date

from app.core.db import db
from app.core.errors import ConflictError, DomainValidationError
from app.models import Contract
from app.repositories import ContractRepository, RoomRepository


class ContractService:
    @staticmethod
    def create_contract(**payload):
        if payload["end_date"] <= payload["start_date"]:
            raise DomainValidationError("合約到期日必須晚於起始日")
        active_contract = ContractRepository.active_for_room(payload["room_id"])
        if active_contract:
            raise ConflictError("此房間已有 active 合約")

        contract = Contract(**payload)
        room = RoomRepository.get_or_404(payload["room_id"])
        room.status = "occupied"
        db.session.add(contract)
        db.session.commit()
        return contract

    @staticmethod
    def update_contract(contract: Contract, **payload):
        if payload["end_date"] <= payload["start_date"]:
            raise DomainValidationError("合約到期日必須晚於起始日")
        active_contract = ContractRepository.active_for_room(payload["room_id"])
        if active_contract and active_contract.id != contract.id:
            raise ConflictError("此房間已有 active 合約")

        previous_room_id = contract.room_id
        for key, value in payload.items():
            setattr(contract, key, value)

        if previous_room_id != contract.room_id:
            old_room = RoomRepository.get_or_404(previous_room_id)
            old_room.status = "vacant"
            new_room = RoomRepository.get_or_404(contract.room_id)
            new_room.status = "occupied"

        db.session.commit()
        return contract

    @staticmethod
    def terminate_contract(contract: Contract):
        contract.status = "terminated"
        room = RoomRepository.get_or_404(contract.room_id)
        room.status = "vacant"
        db.session.commit()
        return contract

    @staticmethod
    def sync_expired_contracts(reference_date: date | None = None):
        ref = reference_date or date.today()
        expired_contracts = Contract.query.filter(Contract.status == "active", Contract.end_date < ref).all()
        for contract in expired_contracts:
            contract.status = "expired"
        db.session.commit()
        return expired_contracts
