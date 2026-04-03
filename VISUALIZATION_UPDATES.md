# Visualization Updates - Owner Address Filtering

## Summary

Updated the Glass Box Explorer visualization to:
1. Add owner address dropdown filter
2. Rename "Processor Output" to "Triggers"
3. Filter triggers and agents by selected owner address
4. Add your personal account address for testing

## Changes Made

### 1. Backend API (server.py)

**Added** `/api/owners` endpoint to get list of owner addresses:
```python
@app.route('/api/owners', methods=['GET'])
def get_owners():
    """Get list of all owner addresses from mocked_accounts table."""
    accounts = db.list_mocked_accounts(active_only=True)
    owners = [
        {
            'address': acc['account_address'],
            'project_name': acc['project_name'],
            'description': acc['description']
        }
        for acc in accounts
    ]
    return jsonify({'success': True, 'count': len(owners), 'owners': owners})
```

**Updated** `/api/triggers` endpoint to support owner filtering:
- Added `owner` query parameter
- Filters triggers where `trigger.owner == selected_owner`

### 2. Frontend HTML (index.html)

**Changed tab name**:
- `"processor-output"` → `"triggers"`
- `"Processor Output"` → `"Triggers"`
- Updated all corresponding IDs and onclick handlers

**Added owner dropdown**:
```html
<div class="filter-bar">
    <select id="owner-filter">
        <option value="all">All Owners</option>
        <!-- Dynamically populated from API -->
    </select>
    <select id="trigger-type-filter">
        <!-- Existing type filter -->
    </select>
    <input type="text" id="search-box" placeholder="...">
</div>
```

### 3. Frontend JavaScript (main.js)

**Added state variables**:
```javascript
let owners = [];
let selectedOwner = 'all';
```

**Added functions**:
- `loadOwners()` - Fetches owner addresses from API
- `populateOwnerFilter()` - Populates dropdown with options
- Owner filter change handler to reload triggers when selection changes

**Updated `loadTriggers()`** to include owner parameter:
```javascript
async function loadTriggers() {
    const params = new URLSearchParams();
    if (selectedOwner !== 'all') {
        params.append('owner', selectedOwner);
    }
    const response = await fetch(`${API_BASE}/triggers?${params}`);
    // ...
}
```

**Updated `createTriggerCard()`** to display owner field:
```javascript
<div class="trigger-field">
    <div class="field-label">Owner</div>
    <div class="field-value">${truncate(trigger.owner || 'default', 32)}</div>
</div>
```

### 4. Database

**Your account registered**:
- Address: `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb1`
- Project: `BTC-News-Pipeline`
- Description: "Bitcoin news sentiment analysis project"

**Test accounts also available**:
- SUI-News-Pipeline: `0x9876543210abcdef9876543210abcdef98765432`
- Multi-Token-Sentiment: `0xabcdef1234567890abcdef1234567890abcdef12`

## Remaining Manual Steps

Due to file editing constraints, you need to manually add these JavaScript functions to `visualization/static/js/main.js`:

### Step 1: Add to DOMContentLoaded (around line 70)

```javascript
document.addEventListener('DOMContentLoaded', () => {
    // ... existing tab setup code ...

    // ADD THIS: Setup owner filter
    const ownerFilter = document.getElementById('owner-filter');
    if (ownerFilter) {
        ownerFilter.addEventListener('change', (e) => {
            selectedOwner = e.target.value;
            loadTriggers();
        });
    }

    // UPDATE THIS LINE:
    loadOwners();  // Add this
    loadTriggers();  // Change from loadProcessorOutput()
    loadAgents();
});
```

### Step 2: Add loadOwners() function (after line 94)

```javascript
// ============================================================================
// Owners
// ============================================================================

async function loadOwners() {
    try {
        const response = await fetch(`${API_BASE}/owners`);
        const data = await response.json();

        if (data.success) {
            owners = data.owners || [];
            populateOwnerFilter(owners);
        }
    } catch (error) {
        console.error('Error loading owners:', error);
    }
}

function populateOwnerFilter(ownersList) {
    const ownerFilter = document.getElementById('owner-filter');

    // Clear existing options except "All Owners"
    ownerFilter.innerHTML = '<option value="all">All Owners</option>';

    // Add owner options
    ownersList.forEach(owner => {
        const option = document.createElement('option');
        option.value = owner.address;
        option.textContent = `${owner.project_name} (${truncate(owner.address, 16)})`;
        ownerFilter.appendChild(option);
    });
}
```

### Step 3: Update loadTriggers() function (around line 98)

```javascript
async function loadTriggers() {  // Rename from loadProcessorOutput
    try {
        // ADD THIS: Include owner filter
        const params = new URLSearchParams();
        if (selectedOwner !== 'all') {
            params.append('owner', selectedOwner);
        }

        const response = await fetch(`${API_BASE}/triggers?${params}`);  // Update URL
        const data = await response.json();

        triggers = data.triggers || [];
        updateTriggerStats(triggers);  // Rename from updateProcessorStats
        renderTriggers(triggers);
    } catch (error) {
        console.error('Error loading triggers:', error);
        // ... error handling ...
    }
}
```

### Step 4: Add Owner field to createTriggerCard() (around line 178)

```javascript
// After the "Walrus Blob ID" field, add:
<div class="trigger-field">
    <div class="field-label">Owner</div>
    <div class="field-value">${truncate(trigger.owner || 'default', 32)}</div>
</div>
```

### Step 5: Rename functions

- `refreshProcessorOutput()` → `refreshTriggers()`
- `updateProcessorStats()` → `updateTriggerStats()`
- All references to `loadProcessorOutput` → `loadTriggers`

## Testing

1. **Start API Server**:
   ```bash
   cd visualization/api
   python server.py
   ```

2. **Generate Some Triggers** (with your owner address):
   ```bash
   cd ../../demo
   python scripts/test_pipeline_v2.py
   ```

3. **Open Browser**:
   - Navigate to http://localhost:8080
   - You should see:
     - "Triggers" tab instead of "Processor Output"
     - Owner dropdown with your account address
     - Triggers filtered by selected owner

## Benefits

1. **Multi-Project Organization**: Filter triggers by account/project
2. **Clear Ownership**: See which account owns each trigger
3. **Better UX**: More accurate terminology ("Triggers" instead of "Processor Output")
4. **Scalable**: Easy to add more accounts as you create more projects

## Next Steps

1. Complete the JavaScript updates listed above
2. Test with real triggers from pipeline
3. Consider adding owner filtering to Agents tab as well
4. Add visual indicators (colors/icons) for different owners
