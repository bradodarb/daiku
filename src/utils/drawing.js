export function drawSegment(ctx, segment, isSelected = false, pathColor = null) {
  ctx.save();
  
  ctx.strokeStyle = pathColor || segment.strokeColor || '#000000';
  ctx.lineWidth = segment.strokeWidth || 2;
  ctx.fillStyle = 'transparent';
  
  if (isSelected) {
    ctx.shadowColor = '#007acc';
    ctx.shadowBlur = 4;
  }
  
  switch (segment.type) {
    case 'line':
      drawLine(ctx, segment);
      break;
    case 'circle':
      drawCircle(ctx, segment);
      break;
    case 'rectangle':
      drawRectangle(ctx, segment);
      break;
    case 'arc':
      drawArc(ctx, segment);
      break;
  }
  
  ctx.restore();
}

function drawLine(ctx, segment) {
  ctx.beginPath();
  ctx.moveTo(segment.x1, segment.y1);
  ctx.lineTo(segment.x2, segment.y2);
  ctx.stroke();
}

function drawCircle(ctx, segment) {
  ctx.beginPath();
  ctx.arc(segment.cx, segment.cy, Math.abs(segment.r), 0, Math.PI * 2);
  ctx.stroke();
}

function drawRectangle(ctx, segment) {
  ctx.beginPath();
  ctx.rect(segment.x, segment.y, segment.width, segment.height);
  ctx.stroke();
}

function drawArc(ctx, segment) {
  ctx.beginPath();
  ctx.arc(segment.cx, segment.cy, Math.abs(segment.r), segment.startAngle, segment.endAngle);
  ctx.stroke();
}

export function hitTestSegment(segment, x, y, threshold = 5) {
  switch (segment.type) {
    case 'line':
      return hitTestLine(segment, x, y, threshold);
    case 'circle':
      return hitTestCircle(segment, x, y, threshold);
    case 'rectangle':
      return hitTestRectangle(segment, x, y, threshold);
    case 'arc':
      return hitTestArc(segment, x, y, threshold);
    default:
      return false;
  }
}

function hitTestLine(segment, x, y, threshold) {
  const { x1, y1, x2, y2 } = segment;
  
  // Calculate distance from point to line
  const A = x - x1;
  const B = y - y1;
  const C = x2 - x1;
  const D = y2 - y1;
  
  const dot = A * C + B * D;
  const lenSq = C * C + D * D;
  let param = -1;
  
  if (lenSq !== 0) {
    param = dot / lenSq;
  }
  
  let xx, yy;
  
  if (param < 0) {
    xx = x1;
    yy = y1;
  } else if (param > 1) {
    xx = x2;
    yy = y2;
  } else {
    xx = x1 + param * C;
    yy = y1 + param * D;
  }
  
  const dx = x - xx;
  const dy = y - yy;
  const distance = Math.sqrt(dx * dx + dy * dy);
  
  return distance <= threshold;
}

function hitTestCircle(segment, x, y, threshold) {
  const { cx, cy, r } = segment;
  const distance = Math.sqrt(Math.pow(x - cx, 2) + Math.pow(y - cy, 2));
  return Math.abs(distance - Math.abs(r)) <= threshold;
}

function hitTestRectangle(segment, x, y, threshold) {
  const { x: rx, y: ry, width, height } = segment;
  
  // Check if point is on any edge
  const onLeft = Math.abs(x - rx) <= threshold && y >= ry - threshold && y <= ry + height + threshold;
  const onRight = Math.abs(x - (rx + width)) <= threshold && y >= ry - threshold && y <= ry + height + threshold;
  const onTop = Math.abs(y - ry) <= threshold && x >= rx - threshold && x <= rx + width + threshold;
  const onBottom = Math.abs(y - (ry + height)) <= threshold && x >= rx - threshold && x <= rx + width + threshold;
  
  return onLeft || onRight || onTop || onBottom;
}

function hitTestArc(segment, x, y, threshold) {
  const { cx, cy, r, startAngle, endAngle } = segment;
  
  // Check if point is on the arc
  const distance = Math.sqrt(Math.pow(x - cx, 2) + Math.pow(y - cy, 2));
  if (Math.abs(distance - Math.abs(r)) > threshold) {
    return false;
  }
  
  // Check if point is within the angle range
  let angle = Math.atan2(y - cy, x - cx);
  
  // Normalize angles to 0-2π range
  let start = normalizeAngle(startAngle);
  let end = normalizeAngle(endAngle);
  angle = normalizeAngle(angle);
  
  // Handle the case where the arc crosses 0 degrees
  if (start > end) {
    return angle >= start || angle <= end;
  } else {
    return angle >= start && angle <= end;
  }
}

function normalizeAngle(angle) {
  while (angle < 0) angle += Math.PI * 2;
  while (angle >= Math.PI * 2) angle -= Math.PI * 2;
  return angle;
}

export function getSegmentBounds(segment) {
  switch (segment.type) {
    case 'line':
      return {
        x: Math.min(segment.x1, segment.x2),
        y: Math.min(segment.y1, segment.y2),
        width: Math.abs(segment.x2 - segment.x1),
        height: Math.abs(segment.y2 - segment.y1)
      };
    case 'circle':
      return {
        x: segment.cx - segment.r,
        y: segment.cy - segment.r,
        width: segment.r * 2,
        height: segment.r * 2
      };
    case 'rectangle':
      return {
        x: segment.x,
        y: segment.y,
        width: segment.width,
        height: segment.height
      };
    case 'arc':
      // Simplified bounds for arc
      return {
        x: segment.cx - segment.r,
        y: segment.cy - segment.r,
        width: segment.r * 2,
        height: segment.r * 2
      };
    default:
      return { x: 0, y: 0, width: 0, height: 0 };
  }
}

// Find shared points between segments
export function findSharedPoints(segment1, segment2, threshold = 10) {
  const points1 = getSegmentPoints(segment1);
  const points2 = getSegmentPoints(segment2);
  const shared = [];
  
  points1.forEach(p1 => {
    points2.forEach(p2 => {
      if (Math.abs(p1.x - p2.x) < threshold && Math.abs(p1.y - p2.y) < threshold) {
        shared.push({
          segment1Point: p1.type,
          segment2Point: p2.type,
          x: (p1.x + p2.x) / 2,
          y: (p1.y + p2.y) / 2
        });
      }
    });
  });
  
  return shared;
}

function getSegmentPoints(segment) {
  const points = [];
  
  switch (segment.type) {
    case 'line':
      points.push({ x: segment.x1, y: segment.y1, type: 'start' });
      points.push({ x: segment.x2, y: segment.y2, type: 'end' });
      break;
    case 'circle':
      // For circles, we consider 4 cardinal points
      points.push({ x: segment.cx + segment.r, y: segment.cy, type: 'right' });
      points.push({ x: segment.cx - segment.r, y: segment.cy, type: 'left' });
      points.push({ x: segment.cx, y: segment.cy + segment.r, type: 'bottom' });
      points.push({ x: segment.cx, y: segment.cy - segment.r, type: 'top' });
      break;
    case 'rectangle':
      points.push({ x: segment.x, y: segment.y, type: 'tl' });
      points.push({ x: segment.x + segment.width, y: segment.y, type: 'tr' });
      points.push({ x: segment.x, y: segment.y + segment.height, type: 'bl' });
      points.push({ x: segment.x + segment.width, y: segment.y + segment.height, type: 'br' });
      break;
    case 'arc':
      const startX = segment.cx + segment.r * Math.cos(segment.startAngle);
      const startY = segment.cy + segment.r * Math.sin(segment.startAngle);
      const endX = segment.cx + segment.r * Math.cos(segment.endAngle);
      const endY = segment.cy + segment.r * Math.sin(segment.endAngle);
      points.push({ x: startX, y: startY, type: 'start' });
      points.push({ x: endX, y: endY, type: 'end' });
      break;
  }
  
  return points;
}

// Update connected segments when a segment is modified
export function updateConnectedSegments(modifiedSegment, allSegments, paths) {
  const updatedSegments = [];
  
  // Find which path contains this segment
  const containingPath = paths.find(p => p.segmentIds.includes(modifiedSegment.id));
  if (!containingPath) return updatedSegments;
  
  // Get all segments in the same path
  const pathSegments = allSegments.filter(s => 
    containingPath.segmentIds.includes(s.id) && s.id !== modifiedSegment.id
  );
  
  // Check each segment in the path for shared points
  pathSegments.forEach(segment => {
    const originalPoints = getSegmentPoints(allSegments.find(s => s.id === segment.id));
    const modifiedPoints = getSegmentPoints(modifiedSegment);
    const sharedBefore = findSharedPoints(
      allSegments.find(s => s.id === segment.id),
      allSegments.find(s => s.id === modifiedSegment.id)
    );
    
    if (sharedBefore.length > 0) {
      // This segment shares points with the modified segment
      const updatedSegment = { ...segment };
      
      sharedBefore.forEach(shared => {
        // Find how the shared point moved
        const oldPoint = originalPoints.find(p => p.type === shared.segment1Point);
        const newPoint = modifiedPoints.find(p => p.type === shared.segment2Point);
        
        if (oldPoint && newPoint) {
          const dx = newPoint.x - shared.x;
          const dy = newPoint.y - shared.y;
          
          // Update the corresponding point in the connected segment
          updateSegmentPoint(updatedSegment, shared.segment1Point, newPoint.x, newPoint.y);
        }
      });
      
      updatedSegments.push(updatedSegment);
    }
  });
  
  return updatedSegments;
}

function updateSegmentPoint(segment, pointType, x, y) {
  switch (segment.type) {
    case 'line':
      if (pointType === 'start') {
        segment.x1 = x;
        segment.y1 = y;
      } else if (pointType === 'end') {
        segment.x2 = x;
        segment.y2 = y;
      }
      break;
    case 'rectangle':
      if (pointType === 'tl') {
        const dx = x - segment.x;
        const dy = y - segment.y;
        segment.x = x;
        segment.y = y;
        segment.width -= dx;
        segment.height -= dy;
      } else if (pointType === 'tr') {
        const dy = y - segment.y;
        segment.y = y;
        segment.width = x - segment.x;
        segment.height -= dy;
      } else if (pointType === 'bl') {
        const dx = x - segment.x;
        segment.x = x;
        segment.width -= dx;
        segment.height = y - segment.y;
      } else if (pointType === 'br') {
        segment.width = x - segment.x;
        segment.height = y - segment.y;
      }
      break;
    case 'arc':
      if (pointType === 'start') {
        segment.startAngle = Math.atan2(y - segment.cy, x - segment.cx);
      } else if (pointType === 'end') {
        segment.endAngle = Math.atan2(y - segment.cy, x - segment.cx);
      }
      break;
  }
}