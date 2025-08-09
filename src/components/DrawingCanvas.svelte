<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import { drawSegment, hitTestSegment, getSegmentBounds, findSharedPoints, updateConnectedSegments } from '../utils/drawing.js';
  
  export let tool = 'select';
  export let segments = [];
  export let paths = [];
  
  const dispatch = createEventDispatcher();
  
  let canvas;
  let ctx;
  let isDrawing = false;
  let isDragging = false;
  let currentSegment = null;
  let selectedSegmentIds = [];
  let dragStart = { x: 0, y: 0 };
  let dragOffset = { x: 0, y: 0 };
  let handles = [];
  let isSelecting = false;
  let selectionBox = null;
  
  onMount(() => {
    ctx = canvas.getContext('2d');
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    return () => {
      window.removeEventListener('resize', resizeCanvas);
    };
  });
  
  function resizeCanvas() {
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
    draw();
  }
  
  function draw() {
    if (!ctx) return;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw all segments
    segments.forEach(segment => {
      const isInPath = paths.some(path => path.segmentIds.includes(segment.id));
      const pathColor = isInPath ? paths.find(p => p.segmentIds.includes(segment.id)).strokeColor : null;
      drawSegment(ctx, segment, selectedSegmentIds.includes(segment.id), pathColor);
    });
    
    // Draw selection box
    if (selectionBox) {
      ctx.strokeStyle = '#007acc';
      ctx.lineWidth = 1;
      ctx.setLineDash([5, 5]);
      ctx.strokeRect(
        selectionBox.x,
        selectionBox.y,
        selectionBox.width,
        selectionBox.height
      );
      ctx.setLineDash([]);
    }
    
    // Draw handles for selected segments
    if (selectedSegmentIds.length === 1) {
      const selectedSegment = segments.find(s => s.id === selectedSegmentIds[0]);
      if (selectedSegment) {
        drawHandles(selectedSegment);
      }
    }
  }
  
  function drawHandles(segment) {
    ctx.fillStyle = '#007acc';
    ctx.strokeStyle = '#007acc';
    
    handles = [];
    
    if (segment.type === 'line') {
      // Start point handle
      drawHandle(segment.x1, segment.y1);
      handles.push({ x: segment.x1, y: segment.y1, property: 'start' });
      
      // End point handle
      drawHandle(segment.x2, segment.y2);
      handles.push({ x: segment.x2, y: segment.y2, property: 'end' });
    } else if (segment.type === 'circle') {
      // Center handle
      drawHandle(segment.cx, segment.cy);
      handles.push({ x: segment.cx, y: segment.cy, property: 'center' });
      
      // Radius handle
      drawHandle(segment.cx + segment.r, segment.cy);
      handles.push({ x: segment.cx + segment.r, y: segment.cy, property: 'radius' });
    } else if (segment.type === 'rectangle') {
      // Corner handles
      drawHandle(segment.x, segment.y);
      handles.push({ x: segment.x, y: segment.y, property: 'tl' });
      
      drawHandle(segment.x + segment.width, segment.y);
      handles.push({ x: segment.x + segment.width, y: segment.y, property: 'tr' });
      
      drawHandle(segment.x, segment.y + segment.height);
      handles.push({ x: segment.x, y: segment.y + segment.height, property: 'bl' });
      
      drawHandle(segment.x + segment.width, segment.y + segment.height);
      handles.push({ x: segment.x + segment.width, y: segment.y + segment.height, property: 'br' });
    } else if (segment.type === 'arc') {
      // Center handle
      drawHandle(segment.cx, segment.cy);
      handles.push({ x: segment.cx, y: segment.cy, property: 'center' });
      
      // Start angle handle
      const startX = segment.cx + segment.r * Math.cos(segment.startAngle);
      const startY = segment.cy + segment.r * Math.sin(segment.startAngle);
      drawHandle(startX, startY);
      handles.push({ x: startX, y: startY, property: 'startAngle' });
      
      // End angle handle
      const endX = segment.cx + segment.r * Math.cos(segment.endAngle);
      const endY = segment.cy + segment.r * Math.sin(segment.endAngle);
      drawHandle(endX, endY);
      handles.push({ x: endX, y: endY, property: 'endAngle' });
    }
  }
  
  function drawHandle(x, y) {
    ctx.beginPath();
    ctx.arc(x, y, 6, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 2;
    ctx.stroke();
  }
  
  function handleMouseDown(event) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    if (tool === 'select') {
      // Check if clicking on a handle (only when single selection)
      if (selectedSegmentIds.length === 1) {
        const handle = getHandleAt(x, y);
        if (handle) {
          isDragging = true;
          dragStart = { x, y };
          currentSegment = segments.find(s => s.id === selectedSegmentIds[0]);
          dragOffset = { handle };
          return;
        }
      }
      
      // Check if clicking on a segment
      const clickedSegment = segments.find(segment => 
        hitTestSegment(segment, x, y)
      );
      
      if (clickedSegment) {
        if (event.shiftKey || event.metaKey) {
          // Multi-select with Shift/Cmd
          if (selectedSegmentIds.includes(clickedSegment.id)) {
            selectedSegmentIds = selectedSegmentIds.filter(id => id !== clickedSegment.id);
          } else {
            selectedSegmentIds = [...selectedSegmentIds, clickedSegment.id];
          }
        } else {
          // Single select
          selectedSegmentIds = [clickedSegment.id];
        }
        
        const selectedSegments = segments.filter(s => selectedSegmentIds.includes(s.id));
        dispatch('segmentSelect', selectedSegments);
        
        isDragging = true;
        dragStart = { x, y };
        
        // Calculate offset from first selected segment reference point
        const firstSegment = selectedSegments[0];
        if (firstSegment.type === 'line') {
          dragOffset = { x: x - firstSegment.x1, y: y - firstSegment.y1 };
        } else if (firstSegment.type === 'circle' || firstSegment.type === 'arc') {
          dragOffset = { x: x - firstSegment.cx, y: y - firstSegment.cy };
        } else if (firstSegment.type === 'rectangle') {
          dragOffset = { x: x - firstSegment.x, y: y - firstSegment.y };
        }
      } else {
        // Start selection box
        isSelecting = true;
        dragStart = { x, y };
        selectionBox = { x, y, width: 0, height: 0 };
        
        if (!event.shiftKey && !event.metaKey) {
          selectedSegmentIds = [];
          dispatch('segmentSelect', []);
        }
      }
    } else {
      // Start drawing new segment
      isDrawing = true;
      dragStart = { x, y };
      
      const newSegment = createSegment(tool, x, y);
      currentSegment = newSegment;
      segments = [...segments, newSegment];
    }
    
    draw();
  }
  
  function handleMouseMove(event) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    if (isDrawing && currentSegment) {
      updateSegmentWhileDrawing(currentSegment, x, y);
      segments = segments.map(s => s.id === currentSegment.id ? currentSegment : s);
      draw();
    } else if (isDragging && selectedSegmentIds.length > 0) {
      if (dragOffset.handle && selectedSegmentIds.length === 1) {
        // Handle dragging for single selection
        const segment = segments.find(s => s.id === selectedSegmentIds[0]);
        if (segment) {
          const connectedSegments = updateSegmentHandle(segment, dragOffset.handle, x, y, segments, paths);
          segments = segments.map(s => {
            const updated = connectedSegments.find(cs => cs.id === s.id);
            return updated || s;
          });
        }
      } else {
        // Move all selected segments
        const dx = x - dragStart.x;
        const dy = y - dragStart.y;
        
        selectedSegmentIds.forEach(id => {
          const segment = segments.find(s => s.id === id);
          if (segment) {
            const tempSegment = { ...segment };
            moveSegment(tempSegment, dx, dy);
            
            // Update connected segments in the same path
            const connectedSegments = updateConnectedSegments(tempSegment, segments, paths);
            segments = segments.map(s => {
              const updated = connectedSegments.find(cs => cs.id === s.id);
              return updated || s;
            });
          }
        });
        
        dragStart = { x, y };
      }
      
      dispatch('segmentsUpdate', segments);
      draw();
    } else if (isSelecting) {
      // Update selection box
      selectionBox = {
        x: Math.min(dragStart.x, x),
        y: Math.min(dragStart.y, y),
        width: Math.abs(x - dragStart.x),
        height: Math.abs(y - dragStart.y)
      };
      draw();
    }
  }
  
  function handleMouseUp() {
    if (isDrawing) {
      isDrawing = false;
      selectedSegmentIds = [currentSegment.id];
      dispatch('segmentSelect', [currentSegment]);
    } else if (isSelecting) {
      // Select all segments within selection box
      if (selectionBox.width > 5 || selectionBox.height > 5) {
        const boxSelectedIds = segments
          .filter(segment => isSegmentInBox(segment, selectionBox))
          .map(s => s.id);
        
        if (boxSelectedIds.length > 0) {
          selectedSegmentIds = [...new Set([...selectedSegmentIds, ...boxSelectedIds])];
          const selectedSegments = segments.filter(s => selectedSegmentIds.includes(s.id));
          dispatch('segmentSelect', selectedSegments);
        }
      }
      
      isSelecting = false;
      selectionBox = null;
    }
    
    isDragging = false;
    currentSegment = null;
    dragOffset = {};
    draw();
  }
  
  function isSegmentInBox(segment, box) {
    const bounds = getSegmentBounds(segment);
    return bounds.x >= box.x && 
           bounds.y >= box.y && 
           bounds.x + bounds.width <= box.x + box.width && 
           bounds.y + bounds.height <= box.y + box.height;
  }
  
  function getHandleAt(x, y) {
    const threshold = 8;
    return handles.find(handle => 
      Math.abs(handle.x - x) < threshold && Math.abs(handle.y - y) < threshold
    );
  }
  
  function createSegment(type, x, y) {
    const id = Date.now().toString();
    const baseProps = {
      id,
      type,
      strokeColor: '#000000',
      strokeWidth: 2
    };
    
    switch (type) {
      case 'line':
        return { ...baseProps, x1: x, y1: y, x2: x, y2: y };
      case 'circle':
        return { ...baseProps, cx: x, cy: y, r: 0 };
      case 'rectangle':
        return { ...baseProps, x, y, width: 0, height: 0 };
      case 'arc':
        return { ...baseProps, cx: x, cy: y, r: 0, startAngle: 0, endAngle: Math.PI / 2 };
      default:
        return null;
    }
  }
  
  function updateSegmentWhileDrawing(segment, x, y) {
    switch (segment.type) {
      case 'line':
        segment.x2 = x;
        segment.y2 = y;
        break;
      case 'circle':
        segment.r = Math.sqrt(Math.pow(x - segment.cx, 2) + Math.pow(y - segment.cy, 2));
        break;
      case 'rectangle':
        segment.width = x - segment.x;
        segment.height = y - segment.y;
        break;
      case 'arc':
        segment.r = Math.sqrt(Math.pow(x - segment.cx, 2) + Math.pow(y - segment.cy, 2));
        break;
    }
  }
  
  function updateSegmentHandle(segment, handle, x, y, allSegments, allPaths) {
    const updatedSegments = [{ ...segment }];
    const threshold = 10;
    
    switch (segment.type) {
      case 'line':
        if (handle.property === 'start') {
          updatedSegments[0].x1 = x;
          updatedSegments[0].y1 = y;
        } else if (handle.property === 'end') {
          updatedSegments[0].x2 = x;
          updatedSegments[0].y2 = y;
        }
        break;
      case 'circle':
        if (handle.property === 'center') {
          updatedSegments[0].cx = x;
          updatedSegments[0].cy = y;
        } else if (handle.property === 'radius') {
          updatedSegments[0].r = Math.sqrt(Math.pow(x - segment.cx, 2) + Math.pow(y - segment.cy, 2));
        }
        break;
      case 'rectangle':
        const prevBounds = { x: segment.x, y: segment.y, width: segment.width, height: segment.height };
        if (handle.property === 'tl') {
          updatedSegments[0].x = x;
          updatedSegments[0].y = y;
          updatedSegments[0].width = prevBounds.x + prevBounds.width - x;
          updatedSegments[0].height = prevBounds.y + prevBounds.height - y;
        } else if (handle.property === 'tr') {
          updatedSegments[0].y = y;
          updatedSegments[0].width = x - segment.x;
          updatedSegments[0].height = prevBounds.y + prevBounds.height - y;
        } else if (handle.property === 'bl') {
          updatedSegments[0].x = x;
          updatedSegments[0].width = prevBounds.x + prevBounds.width - x;
          updatedSegments[0].height = y - segment.y;
        } else if (handle.property === 'br') {
          updatedSegments[0].width = x - segment.x;
          updatedSegments[0].height = y - segment.y;
        }
        break;
      case 'arc':
        if (handle.property === 'center') {
          updatedSegments[0].cx = x;
          updatedSegments[0].cy = y;
        } else if (handle.property === 'startAngle') {
          updatedSegments[0].startAngle = Math.atan2(y - segment.cy, x - segment.cx);
        } else if (handle.property === 'endAngle') {
          updatedSegments[0].endAngle = Math.atan2(y - segment.cy, x - segment.cx);
        }
        break;
    }
    
    // Update connected segments if in a path
    const connectedUpdates = updateConnectedSegments(updatedSegments[0], allSegments, allPaths);
    return [...updatedSegments, ...connectedUpdates.filter(s => s.id !== segment.id)];
  }
  
  function moveSegment(segment, dx, dy) {
    switch (segment.type) {
      case 'line':
        segment.x1 += dx;
        segment.y1 += dy;
        segment.x2 += dx;
        segment.y2 += dy;
        break;
      case 'circle':
      case 'arc':
        segment.cx += dx;
        segment.cy += dy;
        break;
      case 'rectangle':
        segment.x += dx;
        segment.y += dy;
        break;
    }
  }
  
  // Handle keyboard shortcuts
  function handleKeyDown(event) {
    if (event.key === 'Delete' || event.key === 'Backspace') {
      if (selectedSegmentIds.length > 0) {
        segments = segments.filter(s => !selectedSegmentIds.includes(s.id));
        paths = paths.filter(p => 
          p.segmentIds.some(id => segments.some(s => s.id === id))
        );
        selectedSegmentIds = [];
        dispatch('segmentSelect', []);
        dispatch('segmentsUpdate', segments);
        dispatch('pathsUpdate', paths);
        draw();
      }
    }
  }
  
  // Reactive statement to redraw when segments or paths change
  $: segments, paths, draw();
</script>

<svelte:window on:keydown={handleKeyDown} />

<canvas
  bind:this={canvas}
  on:mousedown={handleMouseDown}
  on:mousemove={handleMouseMove}
  on:mouseup={handleMouseUp}
  on:mouseleave={handleMouseUp}
  style="cursor: {tool === 'select' ? 'default' : 'crosshair'}"
/>

<style>
  canvas {
    width: 100%;
    height: 100%;
    display: block;
  }
</style>