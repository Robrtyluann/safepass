"""Valida atualização em PostgreSQL vazio descartável com sufixo *_upgrade_test.

Execute em backend/ com DATABASE_URL. Não usa downgrade, stamp, drop ou create_all.
A segunda execução recusa banco preenchido, sem alterá-lo.
"""

from uuid import uuid4

from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from alembic import command
from app.core.config import get_settings
from app.modules.dependents.models import Dependent
from app.modules.points.models import ManagerAccount
from app.modules.users.models import User


def main() -> None:
    url = get_settings().database_url
    parsed = make_url(url)
    if parsed.get_backend_name() != "postgresql" or not (parsed.database or "").endswith(
        "_upgrade_test"
    ):
        raise RuntimeError("Use somente um PostgreSQL descartável com sufixo _upgrade_test.")
    engine = create_engine(url)
    try:
        if inspect(engine).get_table_names():
            raise RuntimeError("Banco não está vazio; nada foi alterado.")
        config = Config("alembic.ini")
        command.upgrade(config, "66c8e1279f5c")
        user_id, account_id, dependent_id = uuid4(), uuid4(), uuid4()
        with Session(engine) as session:
            session.add(
                User(
                    id=user_id,
                    email="migration@example.com",
                    password_hash="not-a-login-hash",
                    full_name="Migration fixture",
                    role="user",
                )
            )
            session.flush()
            session.add(ManagerAccount(id=account_id, manager_user_id=user_id, balance=37))
            session.flush()
            session.add(
                Dependent(id=dependent_id, account_id=account_id, type="person", name="Fixture")
            )
            session.commit()
        command.upgrade(config, "head")
        command.check(config)
        with Session(engine) as session:
            user = session.get(User, user_id)
            account = session.get(ManagerAccount, account_id)
            dependent = session.get(Dependent, dependent_id)
            assert user is not None and user.email == "migration@example.com"
            assert account is not None and account.balance == 37
            assert dependent is not None and dependent.account_id == account_id
        print("Upgrade preservou usuário, saldo e dependente; alembic check passou.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
