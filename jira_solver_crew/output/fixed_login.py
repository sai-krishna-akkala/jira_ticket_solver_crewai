"""
auth/login.py — fixed version.
Fix: normalize email to lowercase before lookup.
"""

# Simulated user database
USERS_DB = {
	"alice@example.com": {"name": "Alice", "password_hash": "abc123hash"},
	"bob@example.com": {"name": "Bob", "password_hash": "def456hash"},
	"charlie@example.com": {"name": "Charlie", "password_hash": "ghi789hash"},
}


def authenticate(email, password_hash):
	"""Authenticate a user by email and password hash (case-insensitive email)."""
	normalized_email = email.strip().lower()
	user = USERS_DB.get(normalized_email)
	if user is None:
		return {"success": False, "error": "User not found"}

	if user["password_hash"] != password_hash:
		return {"success": False, "error": "Invalid password"}

	return {"success": True, "user": user["name"]}


def login(email, password_hash):
	"""Entry point for login flow."""
	if not email or not password_hash:
		return {"success": False, "error": "Email and password are required"}

	result = authenticate(email, password_hash)
	return result
