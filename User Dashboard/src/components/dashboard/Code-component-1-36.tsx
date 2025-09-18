import React, { useEffect, useRef } from 'react';

export function SystemStatus() {
  const chartRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (chartRef.current) {
      const ctx = chartRef.current.getContext('2d');
      if (ctx) {
        // Simple chart drawing with canvas
        const width = chartRef.current.width;
        const height = chartRef.current.height;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Mock data points for alignment trend
        const dataPoints = [58, 62, 65, 68, 70, 72, 74];
        const maxValue = 80;
        const minValue = 50;
        
        // Set up chart styles
        ctx.strokeStyle = '#F4D03F';
        ctx.lineWidth = 2;
        ctx.fillStyle = 'rgba(244,208,63,0.1)';
        
        // Draw the line chart
        ctx.beginPath();
        dataPoints.forEach((point, index) => {
          const x = (index / (dataPoints.length - 1)) * width;
          const y = height - ((point - minValue) / (maxValue - minValue)) * height;
          
          if (index === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        });
        
        // Fill area under the curve
        const lastX = width;
        const lastY = height - ((dataPoints[dataPoints.length - 1] - minValue) / (maxValue - minValue)) * height;
        ctx.lineTo(lastX, height);
        ctx.lineTo(0, height);
        ctx.closePath();
        ctx.fill();
        
        // Draw the line
        ctx.beginPath();
        dataPoints.forEach((point, index) => {
          const x = (index / (dataPoints.length - 1)) * width;
          const y = height - ((point - minValue) / (maxValue - minValue)) * height;
          
          if (index === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        });
        ctx.stroke();
      }
    }
  }, []);

  return (
    <div className="rounded-2xl border p-5 flex flex-col gap-4" style={{background: 'rgba(26,29,41,0.4)', backdropFilter: 'blur(12px)', borderColor: 'rgba(244,208,63,0.2)'}}>
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold tracking-tight">System Status</h2>
        <span className="text-[11px] px-2 py-1 rounded-full" style={{background: 'rgba(16,185,129,0.15)', color: '#10B981'}}>
          Healthy
        </span>
      </div>
      
      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-lg border p-3" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
          <div className="text-xs" style={{color: '#B8BCC8'}}>Alignment</div>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-lg font-semibold">72%</span>
            <span className="text-[11px] px-1.5 py-0.5 rounded" style={{background: 'rgba(16,185,129,0.15)', color: '#10B981'}}>
              +6%
            </span>
          </div>
        </div>
        <div className="rounded-lg border p-3" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
          <div className="text-xs" style={{color: '#B8BCC8'}}>Focus Budget</div>
          <div className="text-lg font-semibold">5h 20m</div>
        </div>
        <div className="rounded-lg border p-3" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
          <div className="text-xs" style={{color: '#B8BCC8'}}>Tasks Done</div>
          <div className="text-lg font-semibold">14</div>
        </div>
        <div className="rounded-lg border p-3" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
          <div className="text-xs" style={{color: '#B8BCC8'}}>Streak</div>
          <div className="text-lg font-semibold">9 days</div>
        </div>
      </div>

      {/* Mini Chart */}
      <div className="mt-2">
        <h3 className="text-sm font-medium mb-2">Alignment Trend</h3>
        <div className="rounded-xl border p-3" style={{borderColor: 'rgba(244,208,63,0.15)', background: 'rgba(11,13,20,0.35)'}}>
          <div className="h-28">
            <canvas 
              ref={chartRef}
              width={280}
              height={112}
              className="w-full h-full"
            />
          </div>
        </div>
      </div>
    </div>
  );
}