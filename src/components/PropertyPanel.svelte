<script>
  import { createEventDispatcher } from 'svelte';
  
  export let segments = [];
  export let paths = [];
  
  const dispatch = createEventDispatcher();
  
  function updateProperty(segmentId, property, value) {
    dispatch('segmentUpdate', {
      id: segmentId,
      properties: { [property]: parseFloat(value) || 0 }
    });
  }
  
  function updateColor(segmentId, value) {
    dispatch('segmentUpdate', {
      id: segmentId,
      properties: { strokeColor: value }
    });
  }
  
  function updateStrokeWidth(segmentId, value) {
    dispatch('segmentUpdate', {
      id: segmentId,
      properties: { strokeWidth: parseFloat(value) || 1 }
    });
  }
  
  function ungroupPath(pathId) {
    dispatch('ungroupPath', pathId);
  }
  
  // Find which paths contain the selected segments
  $: selectedPaths = paths.filter(path => 
    segments.some(seg => path.segmentIds.includes(seg.id))
  );
</script>

<div class="property-panel">
  <h3>Properties</h3>
  
  {#if segments.length > 0}
    <div class="selection-info">
      <p>{segments.length} segment{segments.length > 1 ? 's' : ''} selected</p>
    </div>
    
    {#if selectedPaths.length > 0}
      <div class="path-info">
        <h4>Grouped in Paths:</h4>
        {#each selectedPaths as path}
          <div class="path-item">
            <span>Path {path.id.slice(-6)}</span>
            <button on:click={() => ungroupPath(path.id)}>Ungroup</button>
          </div>
        {/each}
      </div>
    {/if}
    
    {#if segments.length === 1}
      {@const segment = segments[0]}
      <div class="property-group">
        <h4>{segment.type}</h4>
        
        <div class="property">
          <label>Color:</label>
          <input 
            type="color" 
            value={segment.strokeColor || '#000000'}
            on:change={(e) => updateColor(segment.id, e.target.value)}
          />
        </div>
        
        <div class="property">
          <label>Stroke Width:</label>
          <input 
            type="number" 
            min="1" 
            max="20" 
            value={segment.strokeWidth || 2}
            on:change={(e) => updateStrokeWidth(segment.id, e.target.value)}
          />
        </div>
        
        {#if segment.type === 'line'}
          <div class="property">
            <label>Start X:</label>
            <input 
              type="number" 
              value={segment.x1}
              on:change={(e) => updateProperty(segment.id, 'x1', e.target.value)}
            />
          </div>
          <div class="property">
            <label>Start Y:</label>
            <input 
              type="number" 
              value={segment.y1}
              on:change={(e) => updateProperty(segment.id, 'y1', e.target.value)}
            />
          </div>
          <div class="property">
            <label>End X:</label>
            <input 
              type="number" 
              value={segment.x2}
              on:change={(e) => updateProperty(segment.id, 'x2', e.target.value)}
            />
          </div>
          <div class="property">
            <label>End Y:</label>
            <input 
              type="number" 
              value={segment.y2}
              on:change={(e) => updateProperty(segment.id, 'y2', e.target.value)}
            />
          </div>
        {/if}
        
        {#if segment.type === 'circle'}
          <div class="property">
            <label>Center X:</label>
            <input 
              type="number" 
              value={segment.cx}
              on:change={(e) => updateProperty(segment.id, 'cx', e.target.value)}
            />
          </div>
          <div class="property">
            <label>Center Y:</label>
            <input 
              type="number" 
              value={segment.cy}
              on:change={(e) => updateProperty(segment.id, 'cy', e.target.value)}
            />
          </div>
          <div class="property">
            <label>Radius:</label>
            <input 
              type="number" 
              value={segment.r}
              on:change={(e) => updateProperty(segment.id, 'r', e.target.value)}
            />
          </div>
        {/if}
        
        {#if segment.type === 'rectangle'}
          <div class="property">
            <label>X:</label>
            <input 
              type="number" 
              value={segment.x}
              on:change={(e) => updateProperty(segment.id, 'x', e.target.value)}
            />
          </div>
          <div class="property">
            <label>Y:</label>
            <input 
              type="number" 
              value={segment.y}
              on:change={(e) => updateProperty(segment.id, 'y', e.target.value)}
            />
          </div>
          <div class="property">
            <label>Width:</label>
            <input 
              type="number" 
              value={segment.width}
              on:change={(e) => updateProperty(segment.id, 'width', e.target.value)}
            />
          </div>
          <div class="property">
            <label>Height:</label>
            <input 
              type="number" 
              value={segment.height}
              on:change={(e) => updateProperty(segment.id, 'height', e.target.value)}
            />
          </div>
        {/if}
        
        {#if segment.type === 'arc'}
          <div class="property">
            <label>Center X:</label>
            <input 
              type="number" 
              value={segment.cx}
              on:change={(e) => updateProperty(segment.id, 'cx', e.target.value)}
            />
          </div>
          <div class="property">
            <label>Center Y:</label>
            <input 
              type="number" 
              value={segment.cy}
              on:change={(e) => updateProperty(segment.id, 'cy', e.target.value)}
            />
          </div>
          <div class="property">
            <label>Radius:</label>
            <input 
              type="number" 
              value={segment.r}
              on:change={(e) => updateProperty(segment.id, 'r', e.target.value)}
            />
          </div>
          <div class="property">
            <label>Start Angle:</label>
            <input 
              type="number" 
              value={segment.startAngle * 180 / Math.PI}
              on:change={(e) => updateProperty(segment.id, 'startAngle', e.target.value * Math.PI / 180)}
            />
          </div>
          <div class="property">
            <label>End Angle:</label>
            <input 
              type="number" 
              value={segment.endAngle * 180 / Math.PI}
              on:change={(e) => updateProperty(segment.id, 'endAngle', e.target.value * Math.PI / 180)}
            />
          </div>
        {/if}
      </div>
    {:else}
      <div class="multi-selection">
        <p>Multiple segments selected</p>
        <p class="hint">Properties can be edited when a single segment is selected</p>
      </div>
    {/if}
  {:else}
    <p class="no-selection">No segment selected</p>
  {/if}
</div>

<style>
  .property-panel {
    width: 250px;
    background: white;
    padding: 1rem;
    box-shadow: -2px 0 4px rgba(0,0,0,0.05);
    overflow-y: auto;
  }
  
  .property-panel h3 {
    font-size: 1rem;
    font-weight: 500;
    margin-bottom: 1rem;
    color: #666;
  }
  
  .selection-info {
    padding: 0.5rem;
    background: #f0f0f0;
    border-radius: 4px;
    margin-bottom: 1rem;
    font-size: 0.9rem;
  }
  
  .path-info {
    margin-bottom: 1rem;
    padding: 0.5rem;
    background: #e8f4ff;
    border-radius: 4px;
  }
  
  .path-info h4 {
    font-size: 0.85rem;
    margin-bottom: 0.5rem;
    color: #007acc;
  }
  
  .path-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.25rem 0;
    font-size: 0.85rem;
  }
  
  .path-item button {
    font-size: 0.8rem;
    padding: 2px 8px;
  }
  
  .property-group {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .property-group h4 {
    font-size: 0.9rem;
    font-weight: 500;
    text-transform: capitalize;
    color: #333;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #eee;
  }
  
  .property {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .property label {
    flex: 1;
    font-size: 0.85rem;
    color: #666;
  }
  
  .property input[type="color"] {
    width: 60px;
    height: 30px;
    border: 1px solid #ccc;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .no-selection, .multi-selection {
    color: #999;
    font-size: 0.9rem;
    text-align: center;
    padding: 2rem 0;
  }
  
  .hint {
    font-size: 0.8rem;
    margin-top: 0.5rem;
  }
</style>