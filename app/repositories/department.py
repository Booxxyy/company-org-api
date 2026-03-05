from app.models.department import Department
from app.models.employee import Employee
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentTree, DepartmentRead
from app.schemas.employee import EmployeeRead
from sqlalchemy.orm import Session
from fastapi import HTTPException

def get_or_404(session: Session, department_id: int) -> Department:
    dept = session.get(Department, department_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Подразделение не найдено")
    return dept

def check_unique_name(
        session: Session,
        name: str,
        parent_id: int | None,
        exclude_id: int | None = None,
) -> None:
    query = session.query(Department).filter(
        Department.name == name,
        Department.parent_id == parent_id,
    )
    if exclude_id:
        query = query.filter(Department.id != exclude_id)
    if query.first():
        raise HTTPException(
            status_code=409,
            detail="Подразделение с таким именем уже существует",
        )

def get_subtree_ids(
        session: Session,
        department_id: int,
) -> list[int]:
    result = [department_id]
    children = session.query(Department).filter(
        Department.parent_id == department_id
    ).all()
    for child in children:
        result.extend(get_subtree_ids(session, child.id))
    return result

def check_no_cycles(
        session: Session,
        dept_id: int,
        new_parent_id: int,
) -> None:
    if new_parent_id == dept_id:
        raise HTTPException(
            status_code=409,
            detail="Нельзя сделать подразделение родителем самого себя",
        )
    substree = get_subtree_ids(session, dept_id)
    if new_parent_id in substree:
        raise HTTPException(
            status_code=409,
            detail="Нельзя создать цикл в дереве подразделений",
        )

def create_department(
        session: Session,
        data: DepartmentCreate,
) -> Department:
    if data.parent_id is not None:
        get_or_404(session, data.parent_id)
    check_unique_name(session, data.name, data.parent_id)

    dept = Department(name=data.name, parent_id=data.parent_id)
    session.add(dept)
    session.commit()
    session.refresh(dept)
    return dept

def build_tree(
        session: Session,
        dept: Department,
        current_depth: int,
        max_depth: int,
        include_employees: bool,
) -> DepartmentTree:
    employees = []
    if include_employees:
        emps = session.query(Employee).filter(
            Employee.department_id == dept.id
        ).order_by(Employee.created_at).all()
        employees = [EmployeeRead.model_validate(e) for e in emps]

    children = []
    if current_depth < max_depth:
        child_depts = session.query(Department).filter(
            Department.parent_id == dept.id
        ).all()
        for child in child_depts:
            children.append(
                build_tree(session, child, current_depth + 1, max_depth, include_employees)
            )

    return DepartmentTree(
        employees=employees,
        children=children,
        department=DepartmentRead.model_validate(dept),
    )

def get_department_tree(
        session: Session,
        department_id: int,
        depth: int = 1,
        include_employees: bool = True,
) -> DepartmentTree:
    if depth < 1:
        depth = 1
    if depth > 5:
        depth = 5
    dept = get_or_404(session, department_id)
    return build_tree(session, dept,1, depth, include_employees)

def update_department(
        session: Session,
        department_id: int,
        data: DepartmentUpdate,
) -> Department:
    dept = get_or_404(session, department_id)

    new_name = data.name if data.name is not None else dept.name
    new_parent_id = data.parent_id if data.parent_id is not None else dept.parent_id

    if data.parent_id is not None and data.parent_id != dept.parent_id:
        check_no_cycles(session, department_id, data.parent_id)
        if data.parent_id != -1:
            get_or_404(session, data.parent_id)

    if new_name != dept.name or new_parent_id != dept.parent_id:
        check_unique_name(session, new_name, new_parent_id, exclude_id=department_id)

        dept.name = new_name
        dept.parent_id = new_parent_id
        session.commit()
        session.refresh(dept)
    return dept

def delete_department_cascade(
        session: Session,
        department_id: int,
) -> None:
    dept = get_or_404(session, department_id)
    session.delete(dept)
    session.commit()

def delete_department_reassign(
        session: Session,
        department_id: int,
        reassign_to_id: int,
) -> None:
    dept = get_or_404(session, department_id)
    get_or_404(session, reassign_to_id)

    substree_ids = get_subtree_ids(session, department_id)
    if reassign_to_id in substree_ids:
        raise HTTPException(
            status_code=409,
            detail="Нельзя перевести сотрудников в подразделение внутри удаляемого поддерева",
        )

    session.query(Employee).filter(
        Employee.department_id.in_(substree_ids)
    ).update({"department_id": reassign_to_id}, synchronize_session="fetch")

    session.delete(dept)
    session.commit()