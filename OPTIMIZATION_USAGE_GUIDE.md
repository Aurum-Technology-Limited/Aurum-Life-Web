# Performance Optimization Usage Guide

## 1. React.memo Implementation

### Importing Optimized Components

```jsx
// Import optimized task components
import { TaskItem, TaskList, TaskFilters } from './components/optimized/OptimizedTasks';

// Import optimized chart components
import { 
  OptimizedDonutChart, 
  OptimizedLineChart, 
  OptimizedBarChart 
} from './components/optimized/OptimizedCharts';

// Import optimized list components
import { 
  OptimizedJournalEntryCard,
  OptimizedProjectCard,
  VirtualizedList 
} from './components/optimized/OptimizedLists';
```

### Using Memoized Components

```jsx
// Example: Tasks Page
function TasksPage() {
  const [tasks, setTasks] = useState([]);
  const [filters, setFilters] = useState({});
  
  // Memoize callbacks to prevent re-renders
  const handleToggleComplete = useCallback((taskId) => {
    setTasks(prev => prev.map(task => 
      task.id === taskId ? { ...task, completed: !task.completed } : task
    ));
  }, []);
  
  const handleFilterChange = useCallback((newFilters) => {
    setFilters(newFilters);
  }, []);
  
  // Use optimized components
  return (
    <div>
      <TaskFilters 
        filters={filters}
        onFilterChange={handleFilterChange}
        projects={projects}
      />
      
      <TaskList
        tasks={tasks}
        onToggleComplete={handleToggleComplete}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onViewDetails={handleViewDetails}
      />
    </div>
  );
}
```

### Using Virtual Lists for Large Datasets

```jsx
// For lists with 100+ items
<VirtualizedList
  items={longTaskList}
  itemHeight={80}
  containerHeight={600}
  renderItem={(task) => (
    <TaskItem
      task={task}
      onToggleComplete={handleToggleComplete}
      // ... other props
    />
  )}
/>
```

### Custom Memoization Hook

```jsx
import { useMemorization } from './hooks/useMemorization';

function MyComponent({ data }) {
  // Memoize expensive computation
  const processedData = useComputedValue(() => {
    return expensiveProcessing(data);
  }, [data]);
  
  // Create stable callback
  const handleClick = useStableCallback(() => {
    doSomething(processedData);
  }, [processedData]);
  
  return <div onClick={handleClick}>{/* ... */}</div>;
}
```

## 2. Supabase CDN Implementation

### Basic CDN Image Usage

```jsx
import { CDNImage } from './components/ui/CDNImage';

// Simple CDN image
<CDNImage
  bucket="images"
  path="products/laptop.jpg"
  alt="Product image"
  size="medium"  // thumbnail, small, medium, large
  quality="high" // low, medium, high
  className="rounded-lg"
/>
```

### Responsive CDN Images

```jsx
import { ResponsiveCDNImage } from './components/ui/CDNImage';

// Automatically handles different screen sizes
<ResponsiveCDNImage
  bucket="images"
  path="hero/banner.jpg"
  alt="Hero banner"
  aspectRatio="16/9"
  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
  priority={true} // Load immediately
/>
```

### Avatar Images

```jsx
import { AvatarCDNImage } from './components/ui/CDNImage';

// Optimized avatar with fallback
<AvatarCDNImage
  bucket="avatars"
  path={user.avatar_path}
  alt={user.name}
  size={48} // in pixels
  fallback="/images/default-avatar.png"
/>
```

### Gallery Images

```jsx
import { GalleryCDNImage } from './components/ui/CDNImage';

// Gallery with lightbox support
<div className="grid grid-cols-3 gap-4">
  {images.map(image => (
    <GalleryCDNImage
      key={image.id}
      bucket="images"
      path={image.path}
      alt={image.description}
      caption={image.caption}
      showCaption={true}
      onClick={handleImageClick}
    />
  ))}
</div>
```

### Programmatic CDN Usage

```jsx
import { getSupabaseCDNUrl, getResponsiveImageUrls } from './services/supabaseCDN';

// Get single CDN URL with transformations
const thumbnailUrl = getSupabaseCDNUrl('images', 'product.jpg', {
  width: 200,
  height: 200,
  resize: 'cover',
  quality: 80,
  format: 'webp'
});

// Get all responsive URLs
const urls = getResponsiveImageUrls('images', 'product.jpg');
// urls.original, urls.webp.small, urls.sizes.medium, urls.srcset
```

### Uploading with CDN Optimization

```jsx
import { uploadImageWithCDN } from './services/supabaseCDN';

async function handleImageUpload(file) {
  const result = await uploadImageWithCDN(
    file,
    'images',
    `products/${Date.now()}-${file.name}`
  );
  
  if (result.success) {
    console.log('CDN URLs:', result.urls);
    // Use result.urls.sizes.medium for display
    // Use result.urls.srcset for responsive images
  }
}
```

## 3. Backend CDN Configuration

### Setup CDN Buckets (Run Once)

```python
# In your backend initialization or migration
from storage_cdn_config import setup_cdn_buckets

# Run this to configure buckets
await setup_cdn_buckets()
```

### Upload with CDN Headers

```python
from storage_cdn_config import storage_cdn_config

# Upload image with CDN optimization
result = await storage_cdn_config.upload_with_cdn_optimization(
    bucket_name='images',
    file_path=f'users/{user_id}/profile.jpg',
    file_content=file_bytes,
    content_type='image/jpeg'
)

# Get transformation URL
thumbnail_url = storage_cdn_config.get_transformation_url(
    'images',
    'users/123/profile.jpg',
    {'width': 100, 'height': 100, 'resize': 'cover'}
)
```

## 4. Performance Best Practices

### Component Optimization
1. **Use memo selectively** - Only on components that re-render frequently
2. **Memoize callbacks** - Use useCallback for event handlers
3. **Memoize values** - Use useMemo for expensive computations
4. **Virtual scrolling** - Use VirtualizedList for 100+ items

### Image Optimization
1. **Use appropriate sizes** - Don't load large images for thumbnails
2. **Enable lazy loading** - Use priority={true} only for above-fold images
3. **Provide dimensions** - Always specify width/height to prevent layout shift
4. **Use WebP** - Automatic with CDN transformation

### CDN Best Practices
1. **Cache headers** - Already configured in backend
2. **Responsive images** - Use ResponsiveCDNImage for hero images
3. **Preload critical images** - Use priority prop
4. **Optimize upload size** - Resize before upload if possible

## 5. Migration Guide

### Updating Existing Components

```jsx
// Before
import DonutChart from './components/ui/DonutChart';

// After
import { OptimizedDonutChart } from './components/optimized/OptimizedCharts';

// Before
<img src={imageUrl} alt="Product" />

// After
<CDNImage
  bucket="images"
  path={imagePath}
  alt="Product"
  size="medium"
/>
```

### Gradual Migration
1. Start with heavy components (charts, lists)
2. Update image components to use CDN
3. Add virtual scrolling to long lists
4. Monitor performance improvements

## 6. Performance Monitoring

```jsx
// Use React DevTools Profiler
// 1. Open React DevTools
// 2. Go to Profiler tab
// 3. Start recording
// 4. Interact with your app
// 5. Stop recording and analyze

// Add performance marks
performance.mark('myComponent-start');
// ... component logic
performance.mark('myComponent-end');
performance.measure('myComponent', 'myComponent-start', 'myComponent-end');
```

## Expected Performance Gains

- **React.memo**: 30-50% reduction in unnecessary re-renders
- **CDN Images**: 40-60% faster image loading
- **WebP Format**: 25-35% smaller file sizes
- **Virtual Lists**: Smooth scrolling for 1000+ items
- **Overall**: 2-3x improvement in perceived performance