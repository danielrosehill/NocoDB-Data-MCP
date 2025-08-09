# Enhanced NoCoDB MCP Server - Schema Management Tools

Based on Context7 research of the NoCoDB API, I've significantly enhanced your MCP server with comprehensive schema management capabilities. The `copy_table_to_base` functionality isn't directly supported by NoCoDB's API, but I've added many powerful alternatives.

## New Schema Management Tools

### Table Management

#### `create_table`
Create a new table with custom columns in a base.

**Example Usage:**
```json
{
  "base_id": "base_123",
  "title": "Customer Records",
  "table_name": "customers",
  "columns": [
    {
      "column_name": "name",
      "title": "Customer Name",
      "uidt": "SingleLineText",
      "dt": "varchar"
    },
    {
      "column_name": "email",
      "title": "Email Address", 
      "uidt": "Email",
      "dt": "varchar"
    },
    {
      "column_name": "age",
      "title": "Age",
      "uidt": "Number",
      "dt": "int"
    }
  ]
}
```

#### `delete_table`
Remove a table from a base.

### Column Management

#### `create_column`
Add a new column to an existing table.

**Column Types (uidt):**
- `SingleLineText` - Short text field
- `LongText` - Multi-line text
- `Number` - Numeric values
- `Email` - Email validation
- `URL` - URL validation
- `PhoneNumber` - Phone number
- `Date` - Date picker
- `DateTime` - Date and time
- `Checkbox` - Boolean checkbox
- `SingleSelect` - Dropdown with single choice
- `MultiSelect` - Multiple choice selection
- `Attachment` - File uploads
- `Rating` - Star rating
- `Currency` - Money values
- `Percent` - Percentage values
- `Duration` - Time duration
- `Geometry` - Geographic data
- `JSON` - JSON objects

**Example:**
```json
{
  "table_id": "table_456",
  "column_data": {
    "column_name": "status",
    "title": "Order Status",
    "uidt": "SingleSelect",
    "dt": "varchar",
    "rqd": false
  }
}
```

#### `update_column` & `delete_column`
Modify or remove existing columns.

### View Management

#### `create_view`
Create different view types for tables:
- **Grid** - Spreadsheet-like view
- **Form** - Data entry forms
- **Gallery** - Card-based display
- **Kanban** - Board view with columns

**Example:**
```json
{
  "table_id": "table_456",
  "view_data": {
    "title": "Customer Dashboard",
    "type": "kanban"
  }
}
```

#### `list_views` & `delete_view`
Manage existing views.

### Filter & Sort Management

#### `create_filter`
Add filters to views for data refinement.

**Comparison Operators:**
- `eq` - Equals
- `neq` - Not equals
- `like` - Contains
- `nlike` - Does not contain
- `gt` - Greater than
- `lt` - Less than
- `gte` - Greater than or equal
- `lte` - Less than or equal
- `is` - Is (for null/empty)
- `isnot` - Is not (for null/empty)

**Example:**
```json
{
  "view_id": "view_789",
  "filter_data": {
    "fk_column_id": "col_123",
    "comparison_op": "eq",
    "value": "Active"
  }
}
```

#### `create_sort`
Add sorting to views.

**Example:**
```json
{
  "view_id": "view_789", 
  "sort_data": {
    "fk_column_id": "col_456",
    "direction": "desc"
  }
}
```

### Webhook Management

#### `create_webhook`
Set up automated notifications for table events.

**Webhook Types:**
- `URL` - HTTP POST to endpoint
- `Email` - Email notifications
- `Slack` - Slack messages
- `Discord` - Discord notifications
- `Teams` - Microsoft Teams

**Events:**
- `insert` - New record created
- `update` - Record modified
- `delete` - Record removed

**Timing:**
- `before` - Before operation
- `after` - After operation

**Example:**
```json
{
  "table_id": "table_456",
  "webhook_data": {
    "title": "New Customer Alert",
    "notification": {
      "type": "URL",
      "payload": {
        "url": "https://api.example.com/webhook",
        "method": "POST"
      }
    },
    "event": "after",
    "operation": "insert"
  }
}
```

#### `test_webhook`
Test webhook configurations before deployment.

### Table Duplication

#### `duplicate_table`
Copy a table within the same base (alternative to cross-base copying).

**Example:**
```json
{
  "table_id": "table_456",
  "options": {
    "includeData": true,
    "excludeHooks": false,
    "excludeViews": false
  }
}
```

## Why Copy Table to Base Isn't Supported

The NoCoDB API doesn't provide a direct endpoint for copying tables between different bases. This is likely due to:

1. **Schema Complexity** - Tables may have dependencies and relationships
2. **Permission Models** - Different bases may have different access controls
3. **Data Integrity** - Cross-base operations could create inconsistencies

## Workarounds for Cross-Base Table Copying

1. **Export/Import Approach:**
   - Use `get_table_info` to get schema
   - Use `get_table_data` to export data
   - Use `create_table` to recreate in target base
   - Use `create_record` to import data

2. **Template Approach:**
   - Create table templates with `create_table`
   - Reuse column definitions across bases

3. **Duplication + Manual Move:**
   - Use `duplicate_table` within same base
   - Manually recreate in target base using schema info

## Natural Language Examples

You can now use natural language commands like:

- "Create a new customer table with name, email, and phone columns"
- "Add a status column to the orders table"
- "Create a kanban view for the project tasks"
- "Set up a webhook to notify when new orders are created"
- "Filter the customer view to show only active customers"
- "Sort the products by price in descending order"

## Column Type Reference

| NoCoDB Type | Description | Database Type |
|-------------|-------------|---------------|
| SingleLineText | Short text | varchar |
| LongText | Multi-line text | text |
| Number | Integer/decimal | int/decimal |
| Email | Email validation | varchar |
| URL | URL validation | varchar |
| PhoneNumber | Phone format | varchar |
| Date | Date only | date |
| DateTime | Date and time | datetime |
| Checkbox | True/false | boolean |
| SingleSelect | Dropdown | varchar |
| MultiSelect | Multiple choice | text |
| Attachment | File uploads | text |
| Rating | Star rating | int |
| Currency | Money values | decimal |
| Percent | Percentage | decimal |
| Duration | Time duration | int |
| Geometry | Geographic data | geometry |
| JSON | JSON objects | json |

This enhanced MCP server now provides comprehensive schema management capabilities that go far beyond basic CRUD operations, enabling you to build and manage complex database structures through natural language commands.
