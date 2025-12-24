
// World management functionality

// Load worlds list
async function loadWorlds() {
  try {
    const response = await fetch('/api/worlds?page=1&page_size=100', {
      headers: {
        'Authorization': getAuthToken(),
        'X-User-Id': getUserId()
      }
    });
    
    const result = await response.json();
    
    if (result.code === 0 && result.data && result.data.data) {
      return result.data.data;
    } else {
      console.error('Failed to load worlds:', result.message);
      return [];
    }
  } catch (error) {
    console.error('Error loading worlds:', error);
    return [];
  }
}

// Populate world selector
async function populateWorldSelector() {
  const defaultWorldSelect = document.getElementById('defaultWorldSelect');
  if (!defaultWorldSelect) return;
  
  const worlds = await loadWorlds();
  
  // Clear existing options except the first one
  defaultWorldSelect.innerHTML = '<option value="">选择世界...</option>';
  
  // Add world options
  worlds.forEach(world => {
    const option = document.createElement('option');
    option.value = world.id;
    option.textContent = world.name;
    defaultWorldSelect.appendChild(option);
  });
  
  // Restore saved world selection
  if (state.defaultWorldId) {
    defaultWorldSelect.value = state.defaultWorldId;
  }
}

// Handle world selection change
function handleWorldSelectionChange(worldId) {
  state.defaultWorldId = worldId ? parseInt(worldId) : null;
  
  // Save to workflow
  const workflowId = getWorkflowIdFromUrl();
  if (workflowId) {
    saveDefaultWorld(workflowId, state.defaultWorldId);
  }
  
  console.log('Default world changed to:', state.defaultWorldId);
}

// Save default world to workflow
async function saveDefaultWorld(workflowId, worldId) {
  try {
    const response = await fetch(`/api/video-workflow/${workflowId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': getAuthToken(),
        'X-User-Id': getUserId()
      },
      body: JSON.stringify({
        default_world_id: worldId
      })
    });
    
    const result = await response.json();
    
    if (result.code === 0) {
      console.log('Default world saved successfully');
    } else {
      console.warn('Failed to save default world:', result.message);
    }
  } catch (error) {
    console.error('Error saving default world:', error);
  }
}

// Initialize world selector
function initWorldSelector() {
  const defaultWorldSelect = document.getElementById('defaultWorldSelect');
  if (!defaultWorldSelect) return;
  
  // Load worlds
  populateWorldSelector();
  
  // Handle selection change
  defaultWorldSelect.addEventListener('change', (e) => {
    handleWorldSelectionChange(e.target.value);
  });
}
