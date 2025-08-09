<script>
  import { createEventDispatcher } from 'svelte';
  
  export let tool = 'select';
  
  const dispatch = createEventDispatcher();
  
  const tools = [
    { id: 'select', name: 'Select', icon: '↖' },
    { id: 'line', name: 'Line', icon: '╱' },
    { id: 'arc', name: 'Arc', icon: '⌒' },
    { id: 'circle', name: 'Circle', icon: '○' },
    { id: 'rectangle', name: 'Rectangle', icon: '□' },
  ];
  
  function selectTool(toolId) {
    dispatch('toolChange', toolId);
  }
</script>

<div class="toolbar">
  <h3>Tools</h3>
  {#each tools as t}
    <button 
      class:active={tool === t.id}
      on:click={() => selectTool(t.id)}
      title={t.name}
    >
      <span class="icon">{t.icon}</span>
      <span class="name">{t.name}</span>
    </button>
  {/each}
</div>

<style>
  .toolbar {
    width: 200px;
    background: white;
    padding: 1rem;
    box-shadow: 2px 0 4px rgba(0,0,0,0.05);
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .toolbar h3 {
    font-size: 1rem;
    font-weight: 500;
    margin-bottom: 0.5rem;
    color: #666;
  }
  
  button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    width: 100%;
    text-align: left;
  }
  
  .icon {
    font-size: 1.2rem;
    width: 24px;
    display: inline-block;
    text-align: center;
  }
  
  .name {
    flex: 1;
  }
</style>