<script>
  import DrawingCanvas from './components/DrawingCanvas.svelte';
  import Toolbar from './components/Toolbar.svelte';
  import PropertyPanel from './components/PropertyPanel.svelte';
  
  let tool = 'select';
  let selectedSegments = [];
  let segments = [];
  let paths = [];
  
  function handleToolChange(event) {
    tool = event.detail;
  }
  
  function handleSegmentSelect(event) {
    selectedSegments = event.detail;
  }
  
  function handleSegmentUpdate(event) {
    const { id, properties } = event.detail;
    segments = segments.map(seg => 
      seg.id === id ? { ...seg, ...properties } : seg
    );
  }
  
  function handleSegmentsUpdate(event) {
    segments = event.detail;
  }
  
  function handlePathsUpdate(event) {
    paths = event.detail;
  }
  
  function handleGroupSegments() {
    if (selectedSegments.length < 2) return;
    
    // Create a new path from selected segments
    const newPath = {
      id: Date.now().toString(),
      segmentIds: selectedSegments.map(s => s.id),
      strokeColor: selectedSegments[0].strokeColor || '#000000',
      strokeWidth: selectedSegments[0].strokeWidth || 2
    };
    
    paths = [...paths, newPath];
    selectedSegments = [];
  }
  
  function handleUngroupPath(pathId) {
    paths = paths.filter(p => p.id !== pathId);
  }
  
  $: canGroup = selectedSegments.length >= 2;
</script>

<div class="app">
  <header>
    <h1>Svelte Drawing App</h1>
    {#if canGroup}
      <button class="group-button" on:click={handleGroupSegments}>
        Group Selected Segments
      </button>
    {/if}
  </header>
  
  <div class="main-container">
    <Toolbar {tool} on:toolChange={handleToolChange} />
    
    <div class="canvas-container">
      <DrawingCanvas 
        {tool} 
        bind:segments
        bind:paths
        on:segmentSelect={handleSegmentSelect}
        on:segmentsUpdate={handleSegmentsUpdate}
        on:pathsUpdate={handlePathsUpdate}
      />
    </div>
    
    <PropertyPanel 
      segments={selectedSegments}
      {paths}
      on:segmentUpdate={handleSegmentUpdate}
      on:ungroupPath={handleUngroupPath}
    />
  </div>
</div>

<style>
  .app {
    height: 100vh;
    display: flex;
    flex-direction: column;
  }
  
  header {
    background: #333;
    color: white;
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    display: flex;
    align-items: center;
    gap: 2rem;
  }
  
  header h1 {
    font-size: 1.5rem;
    font-weight: 300;
  }
  
  .group-button {
    background: #007acc;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 14px;
  }
  
  .group-button:hover {
    background: #005a9e;
  }
  
  .main-container {
    flex: 1;
    display: flex;
    overflow: hidden;
  }
  
  .canvas-container {
    flex: 1;
    position: relative;
    background: white;
    margin: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    overflow: hidden;
  }
</style>