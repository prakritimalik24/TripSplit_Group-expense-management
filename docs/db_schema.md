# 1 TripSplit - Database Schema

It is a multi-user group expense management
application. PostgreSQL is used to store user accounts,
groups, expenses, settlements and invitations.

## 2 Database Tables

### 2.1 Users

Stores individual user account info.

id	UUID	Primary Key
name	VARCHAR(100)	NOT NULL
email	VARCHAR(255)	UNIQUE, NOT NULL
password_hash	VARCHAR(255)	NOT NULL
created_at	TIMESTAMPTZ	Default NOW()
updated_at	TIMESTAMPTZ	Default NOW()
is_active	BOOLEAN	Default TRUE

### 2.3 Group Members

Connects users with groups.

| Column | Data Type | Constraints |
|---|---|---|
| id | UUID | Primary Key |
| group_id | UUID | FK -> groups.id |
| user_id | UUID | FK -> users.id |
| role | VARCHAR(20) | DEFAULT member |
| joined_at | TIMESTAMPTZ | DEFAULT NOW() |

Unique constraint: group_id + user_id.

### 2.4 Expenses

Stores expenses added to a group.

| Column | Data Type | Constraints |
|---|---|---|
| id | UUID | Primary Key |
| group_id | UUID | FK -> groups.id |
| paid_by | UUID | FK -> users.id |
| title | VARCHAR(150) | NOT NULL |
| amount | NUMERIC(12,2) | NOT NULL |
| category | VARCHAR(50) | NULL |
| expense_date | TIMESTAMPTZ | NOT NULL |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |

### 2.5 Expense Splits

Stores individual shares of an expense.

| Column | Data Type | Constraints |
|---|---|---|
| id | UUID | Primary Key |
| expense_id | UUID | FK -> expenses.id |
| user_id | UUID | FK -> users.id |
| amount | NUMERIC(12,2) | NOT NULL |

Unique constraint: expense_id + user_id.

### 2.6 Settlements

Records payments between group members.

| Column | Data Type | Constraints |
|---|---|---|
| id | UUID | Primary Key |
| group_id | UUID | FK -> groups.id |
| paid_by | UUID | FK -> users.id |
| paid_to | UUID | FK -> users.id |
| amount | NUMERIC(12,2) | NOT NULL |
| settled_at | TIMESTAMPTZ | DEFAULT NOW() |

### 2.7 Invitations

Stores group invitation information.

| Column | Data Type | Constraints |
|---|---|---|
| id | UUID | Primary Key |
| group_id | UUID | FK -> groups.id |
| invited_by | UUID | FK -> users.id |
| token_hash | VARCHAR(255) | UNIQUE, NOT NULL |
| expires_at | TIMESTAMPTZ | NOT NULL |
| used_at | TIMESTAMPTZ | NULL |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |



## Relationships

1. One user can create multiple groups.
2. Users and groups have a many-to-many relationship
   through group_members.
3. One group can contain multiple expenses.
4. One expense can have multiple expense splits.
5. One user can have multiple expense splits.
6. One group can have multiple settlements.
7. One group can have multiple invitations.

##  Important Rules

- Email addresses must be unique.
- Passwords must be stored as secure hashes.
- Expense amounts must be positive.
- Expense splits must add up to the original expense.
- Only group members can access group information.
- Invitations must use secure, expiring tokens.
- Monetary calculations must use Decimal.