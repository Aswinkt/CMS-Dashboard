# Complaint Management System

A Django-based dashboard with separate login functionality for administrators and employees.

## Features

### Admin Dashboard
- **Total Employee Count**: View the total number of registered employees
- **Total Complaint Count**: See all complaints in the system
- **Complaint Statistics**: Pending, Closed, and Escalated complaint counts
- **User Registration**: Create new employee accounts
- **Complaint Creation**: Create and assign complaints to employees
- **Recent Complaints**: View the latest complaints with details

### Employee Dashboard
- **Assigned Complaints**: View only complaints assigned to the logged-in employee
- **Status Updates**: Change complaint status (Pending, Closed, Escalated)
- **Comments**: Add comments to complaints
- **Real-time Updates**: AJAX-powered status updates

## Setup Instructions

1. **Create a Virtual Environment**:
    ```bash
    python3 -m venv env
    source env/bin/activate  
    ```

2. **Install Dependencies** (if not already installed):
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Run Migrations**:
   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```

4. **Create Superuser** (if not already created):
   ```bash
   python3 manage.py createsuperuser
   ```

5. **Start Development Server**:
   ```bash
   python3 manage.py runserver
   ```

## Usage

### Accessing the System

1. **Open your browser** and go to: `http://127.0.0.1:8002/`

2. **Login Page**: You'll be redirected to the login page at `http://127.0.0.1:8002/login/`

### Admin Access

1. **Login with superuser credentials**:
   - Username: `admin` (or your created superuser)
   - Password: (the password you set during superuser creation)

2. **Admin Dashboard Features**:
   - View statistics cards showing employee and complaint counts
   - Use "Register New User" to create employee accounts
   - Use "Create Complaint" to create and assign complaints
   - View recent complaints in the table

3. **Creating Employee Accounts**:
   - Click "Register New User" in the sidebar
   - Fill in the form with employee details
   - Check "Mark as Employee" to give employee privileges
   - Save the user

4. **Creating Complaints**:
   - Click "Create Complaint" in the sidebar
   - Fill in complaint title and details
   - Assign to an employee from the dropdown
   - Set initial status
   - Save the complaint

### Employee Access

1. **Login with employee credentials** (created by admin)

2. **Employee Dashboard Features**:
   - View only complaints assigned to you
   - Change complaint status using dropdown
   - Add comments to complaints
   - View detailed complaint information

3. **Updating Complaint Status**:
   - Select new status from dropdown
   - Click "Update" button
   - Add optional comments when prompted
   - Status will be updated immediately

## User Types

### Superuser (Admin)
- Full access to all features
- Can create employee accounts
- Can create and assign complaints
- Can view all statistics and complaints

### Employee
- Can only view assigned complaints
- Can update complaint status
- Can add comments to complaints
- Limited access to dashboard features

## Database Models

### User Model
- Extends Django's AbstractUser
- Additional fields: `full_name`, `is_employee`
- Automatic full name generation from first and last name

### Complaints Model
- `title`: Complaint title
- `complaint`: Detailed complaint description
- `assignee`: Employee assigned to handle the complaint
- `status`: Current status (Pending, Closed, Escalated)
- `comments`: Additional notes or updates
- `object_id`: Unique UUID identifier
- Timestamps: `created_date`, `modified_date`

## Security Features

- **Authentication Required**: All dashboard pages require login
- **Role-based Access**: Different views for admin and employees
- **CSRF Protection**: All forms include CSRF tokens
- **Permission Checks**: Views check user permissions before allowing access

## File Structure

```
userDashboard/
├── base/                    # Main app
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── forms.py            # Form classes
│   ├── admin.py            # Admin interface
│   └── urls.py             # URL patterns
├── templates/
│   └── base/               # HTML templates
│       ├── base.html       # Base template
│       ├── login.html      # Login page
│       ├── admin_dashboard.html
│       ├── employee_dashboard.html
│       ├── user_registration.html
│       ├── complaint_create.html
│       └── complaint_detail.html
├── userDashboard/          # Project settings
│   ├── settings.py         # Django settings
│   └── urls.py             # Main URL configuration
└── manage.py              # Django management script
```