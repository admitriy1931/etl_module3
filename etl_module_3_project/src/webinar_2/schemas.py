"""Schema definitions for webinar 2 flattened outputs."""

EMPLOYEE_COLUMNS = [
    "company",
    "department_name",
    "dept_head_first_name",
    "dept_head_last_name",
    "dept_head_email",
    "dept_head_phone",
    "employee_id",
    "employee_first_name",
    "employee_last_name",
    "employee_role",
]

EMPLOYEE_SKILL_COLUMNS = [
    "employee_id",
    "skill",
]

EMPLOYEE_PROJECT_COLUMNS = [
    "employee_id",
    "project_id",
    "project_name",
    "project_status",
]

OFFICE_COLUMNS = [
    "company",
    "city",
    "address",
    "capacity",
]

BOOK_COLUMNS = [
    "store_name",
    "store_city",
    "category_name",
    "book_id",
    "title",
    "author_first_name",
    "author_last_name",
    "price",
    "price_currency",
]

BOOK_TAG_COLUMNS = [
    "book_id",
    "tag",
]

BOOK_REVIEW_COLUMNS = [
    "book_id",
    "review_user",
    "review_rating",
    "review_text",
]
