# TripSplit – Group Expense Management

**TripSplit** is a group expense management application built to make sharing expenses, tracking balances, and settling debts easier among friends and travel groups.

It helps users manage shared expenses transparently without the hassle of manually calculating who owes whom.

## Live Demo

[Try TripSplit Here](https://tripsplitgroup-expense-management-temym2gadlbegftwbodvb2.streamlit.app/)

## Features

- **User Authentication:** Secure user registration and login using password hashing and JWT-based authentication.
- **Persistent Login:** Maintains user login sessions using cookies.
- **Group Management:** Create groups and join existing groups using invitation codes.
- **Expense Management:** Add and manage expenses within a group.
- **Equal Expense Splitting:** Automatically divides an expense equally among selected group members.
- **Custom Expense Splitting:** Allows users to assign individual shares for an expense.
- **Balance Tracking:** Calculates how much each member owes or is owed.
- **Debt Simplification:** Minimizes the number of transactions required to settle group expenses.
- **Settlement Management:** Record settlements between members and view settlement history.
- **Dashboard & Analytics:** Displays expense summaries, personal shares, group information, and spending visualizations.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend logic and expense calculations |
| Streamlit | User interface |
| PostgreSQL | Relational database |
| SQLAlchemy | Database ORM and query management |
| JWT | Authentication and session management |
| Argon2 | Secure password hashing |
| Pandas | Data processing for analytics |
| Matplotlib & Seaborn | Data visualization |
| Extra Streamlit Components | Cookie-based login persistence |
| Git & GitHub | Version control and code management |
| Streamlit Community Cloud | Application deployment |
| Neon | Cloud PostgreSQL database |

## How It Works

1. **Authentication:** Users register or log in to access their accounts.
2. **Group Creation:** A user creates a group and invites other members using an invitation code.
3. **Expense Addition:** Members add expenses and select the participants who share them.
4. **Expense Splitting:** The application calculates equal or custom shares for each participant.
5. **Balance Calculation:** TripSplit calculates each member's net balance based on their contributions and expenses.
6. **Debt Simplification:** A greedy settlement algorithm minimizes the number of payments needed to clear outstanding balances.
7. **Settlement:** Members can record payments and track settlement history.
8. **Analytics:** The dashboard presents spending summaries and visual insights into group expenses.

## Database

TripSplit uses PostgreSQL with SQLAlchemy ORM.

The database contains the following main models:

- User
- Group
- GroupMember
- Expense
- ExpenseSplit
- Settlement
- Invitation

These models manage user accounts, group memberships, shared expenses, individual expense shares, settlements, and group invitations.

---

**Built with Python, Streamlit and PostgreSQL.**