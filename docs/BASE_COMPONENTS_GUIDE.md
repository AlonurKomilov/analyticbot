# Base Components Usage Guide

**Complete reference for all base components in the common component library.**

---

## 📚 Table of Contents

1. [BaseDataTable](#basedatatable)
2. [BaseDialog](#basedialog)
3. [BaseForm](#baseform)
4. [BaseEmptyState](#baseemptystate)
5. [BaseAlert](#basealert)
6. [Best Practices](#best-practices)
7. [Migration Examples](#migration-examples)

---

## BaseDataTable

Reusable data table with sorting, pagination, filtering, row selection, and loading states.

### Import

```typescript
import { BaseDataTable, BaseColumn } from '@/components/common/base';
```

### Basic Usage

```typescript
const columns: BaseColumn<User>[] = [
  { id: 'name', label: 'Name', sortable: true },
  { id: 'email', label: 'Email', sortable: true },
  { id: 'status', label: 'Status', render: (row) => <StatusBadge status={row.status} /> },
];

<BaseDataTable
  columns={columns}
  data={users}
  loading={isLoading}
  pagination={{
    page: 0,
    rowsPerPage: 10,
    totalCount: 100,
    onPageChange: (page) => setPage(page),
  }}
/>
```

### Advanced Features

**Row Selection:**
```typescript
const [selectedRows, setSelectedRows] = useState<Set<string | number>>(new Set());

<BaseDataTable
  columns={columns}
  data={users}
  selectable
  selectedRows={selectedRows}
  onSelectionChange={setSelectedRows}
/>
```

**Sorting:**
```typescript
const [sortBy, setSortBy] = useState<string>('name');
const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

<BaseDataTable
  columns={columns}
  data={users}
  sortBy={sortBy}
  sortDirection={sortDirection}
  onSort={(columnId, direction) => {
    setSortBy(columnId);
    setSortDirection(direction);
  }}
/>
```

**Custom Row Click:**
```typescript
<BaseDataTable
  columns={columns}
  data={users}
  onRowClick={(row, index) => navigate(`/users/${row.id}`)}
/>
```

**Empty State:**
```typescript
<BaseDataTable
  columns={columns}
  data={[]}
  emptyStateTitle="No users found"
  emptyStateDescription="Try adjusting your search criteria"
  emptyStateAction={<Button onClick={handleClearFilters}>Clear Filters</Button>}
/>
```

### Props Reference

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `columns` | `BaseColumn[]` | Required | Column definitions |
| `data` | `T[]` | Required | Data to display |
| `loading` | `boolean` | `false` | Show loading skeleton |
| `sortBy` | `string` | - | Current sort column |
| `sortDirection` | `'asc' \| 'desc'` | `'asc'` | Current sort direction |
| `pagination` | `BasePaginationConfig` | - | Pagination configuration |
| `selectable` | `boolean` | `false` | Enable row selection |
| `selectedRows` | `Set<string \| number>` | `new Set()` | Selected row IDs |
| `onRowClick` | `(row, index) => void` | - | Row click handler |
| `maxHeight` | `string \| number` | - | Max table height |
| `stickyHeader` | `boolean` | `false` | Sticky header |

---

## BaseDialog

Reusable dialog component with consistent layout and behavior.

### Import

```typescript
import { BaseDialog, DialogAction } from '@/components/common/base';
```

### Basic Usage

```typescript
const [open, setOpen] = useState(false);

<BaseDialog
  open={open}
  onClose={() => setOpen(false)}
  title="Confirm Delete"
  content="Are you sure you want to delete this item?"
  actions={{
    cancel: { label: 'Cancel', onClick: () => setOpen(false) },
    confirm: { label: 'Delete', onClick: handleDelete, color: 'error' }
  }}
/>
```

### Advanced Features

**Custom Content:**
```typescript
<BaseDialog
  open={open}
  onClose={() => setOpen(false)}
  title="Edit User"
  size="lg"
>
  <TextField fullWidth label="Name" />
  <TextField fullWidth label="Email" type="email" />
</BaseDialog>
```

**Loading State:**
```typescript
<BaseDialog
  open={open}
  onClose={() => setOpen(false)}
  title="Saving..."
  loading={isSubmitting}
  loadingMessage="Please wait while we save your changes"
/>
```

**With Subtitle:**
```typescript
<BaseDialog
  open={open}
  onClose={() => setOpen(false)}
  title="User Details"
  subtitle="View and edit user information"
  dividers
>
  {/* Content */}
</BaseDialog>
```

**Multiple Actions:**
```typescript
<BaseDialog
  open={open}
  onClose={() => setOpen(false)}
  title="Advanced Options"
  actions={{
    cancel: { label: 'Cancel', onClick: handleCancel },
    additional: [
      { label: 'Reset', onClick: handleReset, variant: 'outlined' },
      { label: 'Preview', onClick: handlePreview, variant: 'outlined' }
    ],
    confirm: { label: 'Save', onClick: handleSave }
  }}
/>
```

### Props Reference

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `open` | `boolean` | Required | Dialog visibility |
| `onClose` | `() => void` | Required | Close handler |
| `title` | `string \| ReactNode` | - | Dialog title |
| `subtitle` | `string` | - | Subtitle text |
| `content` | `ReactNode` | - | Dialog content |
| `actions` | `{ cancel?, confirm?, additional? }` | - | Action buttons |
| `size` | `'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl' \| 'full'` | `'md'` | Dialog size |
| `showCloseButton` | `boolean` | `true` | Show close button |
| `loading` | `boolean` | `false` | Loading state |
| `dividers` | `boolean` | `false` | Show section dividers |

---

## BaseForm

Reusable form component with validation and error handling.

### Import

```typescript
import { BaseForm } from '@/components/common/base';
```

### Basic Usage

```typescript
const handleSubmit = async (event: FormEvent) => {
  // Form submission logic
};

<BaseForm
  onSubmit={handleSubmit}
  onCancel={() => navigate('/back')}
  submitLabel="Save"
>
  <TextField fullWidth name="name" label="Name" required />
  <TextField fullWidth name="email" label="Email" type="email" required />
</BaseForm>
```

### Advanced Features

**With Errors:**
```typescript
const [errors, setErrors] = useState<Record<string, string>>({});

<BaseForm
  onSubmit={handleSubmit}
  error={formError}
  errors={errors}
  loading={isSubmitting}
>
  <TextField
    fullWidth
    name="email"
    label="Email"
    error={!!errors.email}
    helperText={errors.email}
  />
</BaseForm>
```

**Horizontal Layout:**
```typescript
<BaseForm
  onSubmit={handleSubmit}
  direction="row"
  gap="md"
>
  <TextField name="firstName" label="First Name" />
  <TextField name="lastName" label="Last Name" />
</BaseForm>
```

**Custom Actions:**
```typescript
<BaseForm
  onSubmit={handleSubmit}
  submitLabel="Create Account"
  cancelLabel="Go Back"
  actionsPosition="center"
>
  {/* Form fields */}
</BaseForm>
```

### Props Reference

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `children` | `ReactNode` | Required | Form fields |
| `onSubmit` | `(event) => void \| Promise<void>` | Required | Submit handler |
| `onCancel` | `() => void` | - | Cancel handler |
| `submitLabel` | `string` | `'Submit'` | Submit button label |
| `loading` | `boolean` | `false` | Loading state |
| `error` | `string` | - | Form-level error |
| `errors` | `Record<string, string>` | - | Field-level errors |
| `direction` | `'column' \| 'row'` | `'column'` | Form layout |
| `gap` | `'xs' \| 'sm' \| 'md' \| 'lg'` | `'md'` | Field spacing |

---

## BaseEmptyState

Reusable empty state component with icon, title, and action.

### Import

```typescript
import { BaseEmptyState } from '@/components/common/base';
```

### Basic Usage

```typescript
import { SearchIcon } from '@mui/icons-material';

<BaseEmptyState
  icon={<SearchIcon />}
  title="No results found"
  description="Try adjusting your search criteria"
/>
```

### Advanced Features

**With Action Button:**
```typescript
<BaseEmptyState
  icon={<AddIcon />}
  title="No items yet"
  description="Get started by creating your first item"
  action={<Button variant="contained" onClick={handleCreate}>Create Item</Button>}
/>
```

**Compact Version:**
```typescript
<BaseEmptyState
  icon={<InboxIcon />}
  title="Empty inbox"
  compact
/>
```

**Custom Icon Size:**
```typescript
<BaseEmptyState
  icon={<CloudOffIcon />}
  iconSize="xl"
  title="No connection"
  description="Please check your internet connection"
/>
```

### Props Reference

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `icon` | `ReactNode` | `<InboxIcon />` | Icon or illustration |
| `iconSize` | `'sm' \| 'md' \| 'lg' \| 'xl'` | `'lg'` | Icon size |
| `title` | `string` | `'No data'` | Title text |
| `description` | `string` | - | Description text |
| `action` | `ReactNode` | - | Action button |
| `compact` | `boolean` | `false` | Compact layout |
| `minHeight` | `string \| number` | `'400px'` | Minimum height |

---

## BaseAlert

Reusable alert component with severity variants.

### Import

```typescript
import { BaseAlert, AlertSeverity } from '@/components/common/base';
```

### Basic Usage

```typescript
<BaseAlert
  severity="success"
  message="Your changes have been saved successfully"
/>
```

### Advanced Features

**With Title:**
```typescript
<BaseAlert
  severity="error"
  title="Validation Error"
  message="Please fix the errors before submitting"
/>
```

**Dismissible:**
```typescript
const [show, setShow] = useState(true);

{show && (
  <BaseAlert
    severity="info"
    message="New features are available"
    dismissible
    onDismiss={() => setShow(false)}
  />
)}
```

**Auto-Dismiss:**
```typescript
<BaseAlert
  severity="success"
  message="File uploaded successfully"
  autoDismiss
  autoDismissDuration={3000}
  onDismiss={handleDismiss}
/>
```

**With Action:**
```typescript
<BaseAlert
  severity="warning"
  title="Update Available"
  message="A new version is available"
  action={{
    label: 'Update Now',
    onClick: handleUpdate
  }}
/>
```

**Variants:**
```typescript
<BaseAlert severity="info" variant="filled" message="Filled variant" />
<BaseAlert severity="success" variant="outlined" message="Outlined variant" />
<BaseAlert severity="warning" variant="standard" message="Standard variant" />
```

### Props Reference

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `severity` | `'info' \| 'success' \| 'warning' \| 'error'` | Required | Alert severity |
| `message` | `string \| ReactNode` | Required | Alert message |
| `title` | `string` | - | Alert title |
| `dismissible` | `boolean` | `false` | Show dismiss button |
| `onDismiss` | `() => void` | - | Dismiss handler |
| `autoDismiss` | `boolean` | `false` | Auto-dismiss |
| `autoDismissDuration` | `number` | `5000` | Auto-dismiss delay (ms) |
| `variant` | `'standard' \| 'filled' \| 'outlined'` | `'standard'` | Alert variant |
| `action` | `AlertAction` | - | Action button |

---

## Best Practices

### ✅ DO

1. **Use base components for consistency**
   ```typescript
   // Good - Uses base component
   <BaseDialog open={open} onClose={handleClose} title="Confirm" />
   
   // Avoid - Custom implementation
   <Dialog><DialogTitle>Confirm</DialogTitle>...</Dialog>
   ```

2. **Leverage built-in features**
   ```typescript
   // Good - Uses built-in loading state
   <BaseForm onSubmit={handleSubmit} loading={isSubmitting} />
   
   // Avoid - Custom loading logic
   <form>{isSubmitting ? <Spinner /> : <FormFields />}</form>
   ```

3. **Use semantic props**
   ```typescript
   // Good - Clear intent
   <BaseAlert severity="error" message="Invalid input" />
   
   // Avoid - Generic styling
   <Box sx={{ color: 'red' }}>Invalid input</Box>
   ```

### ❌ DON'T

1. **Don't override base component styles**
   ```typescript
   // Bad - Overriding styles defeats the purpose
   <BaseDialog sx={{ '& .MuiDialog-paper': { background: 'red' } }} />
   
   // Good - Use built-in props
   <BaseDialog size="lg" />
   ```

2. **Don't create duplicate patterns**
   ```typescript
   // Bad - Reimplementing existing functionality
   const MyCustomDialog = () => <Dialog>...</Dialog>
   
   // Good - Use base component
   <BaseDialog />
   ```

---

## Migration Examples

### Migrating UserManagement Table

**Before:**
```typescript
<TableContainer>
  <Table>
    <TableHead>
      <TableRow>
        <TableCell>Name</TableCell>
        <TableCell>Email</TableCell>
        <TableCell>Status</TableCell>
      </TableRow>
    </TableHead>
    <TableBody>
      {users.map(user => (
        <TableRow key={user.id}>
          <TableCell>{user.name}</TableCell>
          <TableCell>{user.email}</TableCell>
          <TableCell>{user.status}</TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
  <TablePagination ... />
</TableContainer>
```

**After:**
```typescript
<BaseDataTable
  columns={[
    { id: 'name', label: 'Name', sortable: true },
    { id: 'email', label: 'Email', sortable: true },
    { id: 'status', label: 'Status', render: (row) => <StatusChip status={row.status} /> }
  ]}
  data={users}
  loading={isLoading}
  pagination={{
    page,
    rowsPerPage,
    totalCount,
    onPageChange: setPage
  }}
/>
```

### Migrating Delete Confirmation Dialog

**Before:**
```typescript
<Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
  <DialogTitle>Confirm Delete</DialogTitle>
  <DialogContent>
    Are you sure you want to delete this item?
  </DialogContent>
  <DialogActions>
    <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
    <Button color="error" onClick={handleDelete}>Delete</Button>
  </DialogActions>
</Dialog>
```

**After:**
```typescript
<BaseDialog
  open={deleteDialogOpen}
  onClose={() => setDeleteDialogOpen(false)}
  title="Confirm Delete"
  content="Are you sure you want to delete this item?"
  actions={{
    cancel: { label: 'Cancel', onClick: () => setDeleteDialogOpen(false) },
    confirm: { label: 'Delete', onClick: handleDelete, color: 'error' }
  }}
/>
```

---

## Testing Base Components

All base components include:
- ✅ TypeScript type safety
- ✅ Accessibility (WCAG AAA compliant)
- ✅ Keyboard navigation
- ✅ Screen reader support
- ✅ Responsive design
- ✅ Design token consistency

---

**Last Updated:** October 23, 2025  
**Questions?** Check the component source code or ask the team!
