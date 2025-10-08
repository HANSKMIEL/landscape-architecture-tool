import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Search,
  Trash2,
  Lock,
  Unlock,
  Upload,
  Download,
  AlertCircle,
  CheckCircle,
  UserPlus,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './ui/dialog';

const INITIAL_CREATE_FORM = {
  username: '',
  email: '',
  password: '',
  role: 'user',
  first_name: '',
  last_name: '',
  phone: '',
  company: '',
  notes: '',
};

const CSV_TEMPLATE = `username,email,password,role,first_name,last_name,phone,company,notes\njohn.doe,john@example.com,password123,user,John,Doe,+1234567890,Example Corp,Sample user\njane.admin,jane@example.com,,admin,Jane,Smith,,Admin Corp,Admin user with generated password`;

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [showBulkImport, setShowBulkImport] = useState(false);
  const [createUserForm, setCreateUserForm] = useState(INITIAL_CREATE_FORM);
  const [bulkImportFile, setBulkImportFile] = useState(null);
  const [bulkImportLoading, setBulkImportLoading] = useState(false);
  const [bulkImportResults, setBulkImportResults] = useState(null);

  const roleOptions = useMemo(
    () => [
      { value: 'client', label: 'Client', color: 'bg-blue-100 text-blue-800' },
      { value: 'user', label: 'User', color: 'bg-gray-100 text-gray-800' },
      { value: 'admin', label: 'Admin', color: 'bg-green-100 text-green-800' },
      { value: 'sysadmin', label: 'System Admin', color: 'bg-purple-100 text-purple-800' },
      { value: 'developer', label: 'Developer', color: 'bg-red-100 text-red-800' },
    ],
    [],
  );

  const clearFeedback = useCallback(() => {
    setError('');
    setSuccess('');
  }, []);

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);

      const params = new URLSearchParams({
        page: String(currentPage),
        per_page: '20',
      });

      const trimmedSearch = searchTerm.trim();
      if (trimmedSearch) {
        params.set('search', trimmedSearch);
      }
      if (roleFilter !== 'all') {
        params.set('role', roleFilter);
      }

      const response = await fetch(`/api/users?${params.toString()}`);
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch users');
      }

      setUsers(data.users || []);
      setTotalPages(data.pages || 1);
      setError('');
    } catch (err) {
      console.error('Failed to fetch users:', err);
      setError(err.message || 'Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [currentPage, roleFilter, searchTerm]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleCreateUser = async (event) => {
    event.preventDefault();
    clearFeedback();

    try {
      const response = await fetch('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(createUserForm),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.error || 'Failed to create user');
      }

      setSuccess('User created successfully');
      setShowCreateUser(false);
      setCreateUserForm(INITIAL_CREATE_FORM);
      await fetchUsers();
    } catch (err) {
      console.error('Failed to create user:', err);
      setError(err.message || 'Network error. Please try again.');
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) {
      return;
    }

    clearFeedback();

    try {
      const response = await fetch(`/api/users/${userId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.error || 'Failed to delete user');
      }

      setSuccess('User deleted successfully');
      await fetchUsers();
    } catch (err) {
      console.error('Failed to delete user:', err);
      setError(err.message || 'Network error. Please try again.');
    }
  };

  const handleResetPassword = async (userId) => {
    if (!window.confirm("Are you sure you want to reset this user's password?")) {
      return;
    }

    clearFeedback();

    try {
      const response = await fetch(`/api/users/${userId}/reset-password`, {
        method: 'POST',
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.error || 'Failed to reset password');
      }

      setSuccess(`Password reset. Temporary password: ${data.temporary_password}`);
    } catch (err) {
      console.error('Failed to reset password:', err);
      setError(err.message || 'Network error. Please try again.');
    }
  };

  const handleUnlockAccount = async (userId) => {
    clearFeedback();

    try {
      const response = await fetch(`/api/users/${userId}/unlock`, {
        method: 'POST',
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.error || 'Failed to unlock account');
      }

      setSuccess('Account unlocked successfully');
      await fetchUsers();
    } catch (err) {
      console.error('Failed to unlock account:', err);
      setError(err.message || 'Network error. Please try again.');
    }
  };

  const handleBulkImport = async (event) => {
    event.preventDefault();

    if (!bulkImportFile) {
      return;
    }

    clearFeedback();
    setBulkImportLoading(true);

    try {
      const formData = new FormData();
      formData.append('file', bulkImportFile);

      const response = await fetch('/api/users/bulk-import', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.error || 'Failed to import users');
      }

      setBulkImportResults(data);
      setSuccess(`Bulk import completed: ${data.total_created} users created`);
      setBulkImportFile(null);
      await fetchUsers();
    } catch (err) {
      console.error('Failed to import users:', err);
      setError(err.message || 'Network error. Please try again.');
    } finally {
      setBulkImportLoading(false);
    }
  };

  const downloadCSVTemplate = () => {
    const blob = new Blob([CSV_TEMPLATE], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = 'user_import_template.csv';
    link.click();

    window.URL.revokeObjectURL(url);
  };

  const getRoleBadge = (role) => {
    const roleConfig = roleOptions.find((option) => option.value === role) || roleOptions[1];
    return <Badge className={roleConfig.color}>{roleConfig.label}</Badge>;
  };

  const formatDate = (value) => {
    if (!value) {
      return 'Never';
    }
    return new Date(value).toLocaleDateString();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
          <p className="text-gray-600">Manage users, roles, and permissions</p>
        </div>
        <div className="flex space-x-2">
          <Button onClick={() => setShowBulkImport(true)} variant="outline">
            <Upload className="h-4 w-4 mr-2" />
            Bulk Import
          </Button>
          <Button onClick={() => setShowCreateUser(true)}>
            <UserPlus className="h-4 w-4 mr-2" />
            Add User
          </Button>
        </div>
      </div>

      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      <Card>
        <CardContent className="pt-6">
          <div className="flex space-x-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search users..."
                  value={searchTerm}
                  onChange={(event) => setSearchTerm(event.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={roleFilter} onValueChange={setRoleFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by role" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Roles</SelectItem>
                {roleOptions.map((role) => (
                  <SelectItem key={role.value} value={role.value}>
                    {role.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Users ({users.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading users...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4">User</th>
                    <th className="text-left py-3 px-4">Role</th>
                    <th className="text-left py-3 px-4">Status</th>
                    <th className="text-left py-3 px-4">Last Login</th>
                    <th className="text-left py-3 px-4">Created</th>
                    <th className="text-right py-3 px-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id} className="border-b hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div>
                          <div className="font-medium">{user.full_name || user.username}</div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                          {user.company && (
                            <div className="text-xs text-gray-400">{user.company}</div>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4">{getRoleBadge(user.role)}</td>
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-2">
                          {user.is_active ? (
                            <Badge className="bg-green-100 text-green-800">Active</Badge>
                          ) : (
                            <Badge className="bg-red-100 text-red-800">Inactive</Badge>
                          )}
                          {user.is_locked && (
                            <Badge className="bg-yellow-100 text-yellow-800">Locked</Badge>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4 text-sm text-gray-600">{formatDate(user.last_login)}</td>
                      <td className="py-3 px-4 text-sm text-gray-600">{formatDate(user.created_at)}</td>
                      <td className="py-3 px-4">
                        <div className="flex justify-end space-x-2">
                          <Button size="sm" variant="outline" onClick={() => handleResetPassword(user.id)}>
                            <Lock className="h-4 w-4" />
                          </Button>
                          {user.is_locked && (
                            <Button size="sm" variant="outline" onClick={() => handleUnlockAccount(user.id)}>
                              <Unlock className="h-4 w-4" />
                            </Button>
                          )}
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleDeleteUser(user.id)}
                            className="text-red-600 hover:text-red-800"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {totalPages > 1 && (
            <div className="flex justify-center space-x-2 mt-6">
              <Button variant="outline" disabled={currentPage === 1} onClick={() => setCurrentPage(currentPage - 1)}>
                Previous
              </Button>
              <span className="flex items-center px-4">Page {currentPage} of {totalPages}</span>
              <Button
                variant="outline"
                disabled={currentPage === totalPages}
                onClick={() => setCurrentPage(currentPage + 1)}
              >
                Next
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={showCreateUser} onOpenChange={setShowCreateUser}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Create New User</DialogTitle>
            <DialogDescription>
              Add a new user to the system. Leave password empty to generate a temporary password.
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCreateUser} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="username">Username *</Label>
                <Input
                  id="username"
                  value={createUserForm.username}
                  onChange={(event) =>
                    setCreateUserForm((prev) => ({ ...prev, username: event.target.value }))
                  }
                  required
                />
              </div>
              <div>
                <Label htmlFor="email">Email *</Label>
                <Input
                  id="email"
                  type="email"
                  value={createUserForm.email}
                  onChange={(event) => setCreateUserForm((prev) => ({ ...prev, email: event.target.value }))}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={createUserForm.password}
                  onChange={(event) =>
                    setCreateUserForm((prev) => ({ ...prev, password: event.target.value }))
                  }
                  placeholder="Leave empty for auto-generated"
                />
              </div>
              <div>
                <Label htmlFor="role">Role</Label>
                <Select
                  value={createUserForm.role}
                  onValueChange={(value) => setCreateUserForm((prev) => ({ ...prev, role: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a role" />
                  </SelectTrigger>
                  <SelectContent>
                    {roleOptions.map((role) => (
                      <SelectItem key={role.value} value={role.value}>
                        {role.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="first_name">First Name</Label>
                <Input
                  id="first_name"
                  value={createUserForm.first_name}
                  onChange={(event) =>
                    setCreateUserForm((prev) => ({ ...prev, first_name: event.target.value }))
                  }
                />
              </div>
              <div>
                <Label htmlFor="last_name">Last Name</Label>
                <Input
                  id="last_name"
                  value={createUserForm.last_name}
                  onChange={(event) =>
                    setCreateUserForm((prev) => ({ ...prev, last_name: event.target.value }))
                  }
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="phone">Phone</Label>
                <Input
                  id="phone"
                  value={createUserForm.phone}
                  onChange={(event) => setCreateUserForm((prev) => ({ ...prev, phone: event.target.value }))}
                />
              </div>
              <div>
                <Label htmlFor="company">Company</Label>
                <Input
                  id="company"
                  value={createUserForm.company}
                  onChange={(event) =>
                    setCreateUserForm((prev) => ({ ...prev, company: event.target.value }))
                  }
                />
              </div>
            </div>

            <div>
              <Label htmlFor="notes">Notes</Label>
              <textarea
                id="notes"
                className="w-full p-2 border rounded-md"
                rows={3}
                value={createUserForm.notes}
                onChange={(event) => setCreateUserForm((prev) => ({ ...prev, notes: event.target.value }))}
              />
            </div>

            <div className="flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={() => setShowCreateUser(false)}>
                Cancel
              </Button>
              <Button type="submit">Create User</Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={showBulkImport} onOpenChange={setShowBulkImport}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Bulk Import Users</DialogTitle>
            <DialogDescription>Upload a CSV file to import multiple users at once.</DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <Button onClick={downloadCSVTemplate} variant="outline" className="w-full">
                <Download className="h-4 w-4 mr-2" />
                Download CSV Template
              </Button>
            </div>

            <form onSubmit={handleBulkImport} className="space-y-4">
              <div>
                <Label htmlFor="csvFile">CSV File</Label>
                <Input
                  id="csvFile"
                  type="file"
                  accept=".csv"
                  onChange={(event) => setBulkImportFile(event.target.files?.[0] ?? null)}
                  required
                />
              </div>

              {bulkImportResults && (
                <div className="space-y-2">
                  <h4 className="font-medium">Import Results:</h4>
                  <div className="text-sm">
                    <div className="text-green-600">✓ Created: {bulkImportResults.total_created} users</div>
                    <div className="text-red-600">✗ Errors: {bulkImportResults.total_errors}</div>
                    {(bulkImportResults.errors || []).length > 0 && (
                      <div className="mt-2">
                        <details>
                          <summary className="cursor-pointer">View Errors</summary>
                          <ul className="mt-1 text-xs text-red-600">
                            {bulkImportResults.errors.map((err, index) => (
                              <li key={index}>• {err}</li>
                            ))}
                          </ul>
                        </details>
                      </div>
                    )}
                  </div>
                </div>
              )}

              <div className="flex justify-end space-x-2">
                <Button type="button" variant="outline" onClick={() => setShowBulkImport(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={bulkImportLoading || !bulkImportFile}>
                  {bulkImportLoading ? 'Importing...' : 'Import Users'}
                </Button>
              </div>
            </form>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default UserManagement;
