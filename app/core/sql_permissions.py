from app.utils.enums import Permission

PERMISSION_SQL_MAP = {
    Permission.SELECT_ONLY: ["SELECT"],
    Permission.READ_WRITE: ["SELECT", "INSERT"],
    Permission.ADMIN_ACCESS: ["SELECT", "INSERT", "UPDATE", "DELETE", "ALTER", "DROP"]
}