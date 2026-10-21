from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.database import Base
from app.modules.providers.models import (
    Category,
    Professional,
    ProfessionalLink,
    Provider,
    ProviderService,
    ServiceDefinition,
    ServiceRequest,
    Tag,
)
from app.shared.pagination import paginate


class ProviderRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, record: Base) -> None:
        self.session.add(record)
        self.session.flush()

    def get(self, provider_id: UUID) -> Provider | None:
        return self.session.scalar(
            select(Provider).where(Provider.id == provider_id).with_for_update()
        )

    def membership(self, provider_id: UUID, user_id: UUID) -> ProfessionalLink | None:
        return self.session.scalar(
            select(ProfessionalLink)
            .join(Professional)
            .where(
                ProfessionalLink.provider_id == provider_id,
                Professional.user_id == user_id,
                ProfessionalLink.active.is_(True),
            )
        )

    def list_providers(
        self, user_id: UUID | None, public: bool, admin: bool, page: int, size: int
    ) -> tuple[list[Provider], int]:
        query = select(Provider).order_by(Provider.display_name, Provider.id)
        if public:
            query = query.where(Provider.status == "approved")
        elif not admin:
            linked = (
                select(ProfessionalLink.provider_id)
                .join(Professional)
                .where(Professional.user_id == user_id, ProfessionalLink.active.is_(True))
            )
            query = query.where(or_(Provider.owner_user_id == user_id, Provider.id.in_(linked)))
        return paginate(self.session, query, page, size)

    def categories(self, page: int, size: int) -> tuple[list[Category], int]:
        return paginate(
            self.session,
            select(Category).where(Category.active).order_by(Category.name),
            page,
            size,
        )

    def tags(self, page: int, size: int) -> tuple[list[Tag], int]:
        return paginate(self.session, select(Tag).where(Tag.active).order_by(Tag.name), page, size)

    def category(self, category_id: UUID) -> Category | None:
        return self.session.get(Category, category_id)

    def tag(self, tag_id: UUID) -> Tag | None:
        return self.session.get(Tag, tag_id)

    def definition(self, service_id: UUID) -> ServiceDefinition | None:
        return self.session.get(ServiceDefinition, service_id)

    def definitions(self, page: int, size: int, search: str) -> tuple[list[ServiceDefinition], int]:
        query = select(ServiceDefinition).where(ServiceDefinition.active)
        if search:
            query = query.where(ServiceDefinition.name.icontains(search, autoescape=True))
        return paginate(self.session, query.order_by(ServiceDefinition.name), page, size)

    def services(
        self, provider_id: UUID, page: int, size: int
    ) -> tuple[list[ProviderService], int]:
        return paginate(
            self.session,
            select(ProviderService)
            .where(ProviderService.provider_id == provider_id)
            .order_by(ProviderService.id),
            page,
            size,
        )

    def public_services(
        self, provider_id: UUID, page: int, size: int
    ) -> tuple[list[ProviderService], int]:
        query = (
            select(ProviderService)
            .join(ServiceDefinition)
            .where(
                ProviderService.provider_id == provider_id,
                ProviderService.active,
                ServiceDefinition.active,
            )
            .order_by(ProviderService.id)
        )
        return paginate(self.session, query, page, size)

    def service(self, provider_id: UUID, link_id: UUID) -> ProviderService | None:
        return self.session.scalar(
            select(ProviderService).where(
                ProviderService.id == link_id, ProviderService.provider_id == provider_id
            )
        )

    def request(self, provider_id: UUID, request_id: UUID) -> ServiceRequest | None:
        return self.session.scalar(
            select(ServiceRequest).where(
                ServiceRequest.id == request_id, ServiceRequest.provider_id == provider_id
            )
        )

    def requests(self, provider_id: UUID, page: int, size: int) -> tuple[list[ServiceRequest], int]:
        return paginate(
            self.session,
            select(ServiceRequest)
            .where(ServiceRequest.provider_id == provider_id)
            .order_by(ServiceRequest.created_at),
            page,
            size,
        )

    def professional(self, professional_id: UUID) -> Professional | None:
        return self.session.get(Professional, professional_id)

    def link(self, provider_id: UUID, link_id: UUID) -> ProfessionalLink | None:
        return self.session.scalar(
            select(ProfessionalLink).where(
                ProfessionalLink.id == link_id, ProfessionalLink.provider_id == provider_id
            )
        )

    def links(self, provider_id: UUID, page: int, size: int) -> tuple[list[ProfessionalLink], int]:
        return paginate(
            self.session,
            select(ProfessionalLink)
            .where(ProfessionalLink.provider_id == provider_id)
            .order_by(ProfessionalLink.created_at),
            page,
            size,
        )
