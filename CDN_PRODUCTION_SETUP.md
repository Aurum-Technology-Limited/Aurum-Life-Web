# CDN Production Setup Guide

## Prerequisites
- Supabase project with storage enabled
- Admin access to Supabase dashboard
- Frontend deployed with environment variables

## Step 1: Run Bucket Setup SQL

1. Go to Supabase Dashboard → SQL Editor
2. Copy and paste the contents of `SUPABASE_BUCKET_SETUP.sql`
3. Click "Run" to execute
4. Verify success in the output

## Step 2: Upload Initial Assets

### Logo and Static Assets
```bash
# Using Supabase CLI
supabase storage upload assets/logos/aurum-brain-logo.svg ./public/aurum-brain-logo.svg

# Or using the Dashboard:
# 1. Go to Storage → assets bucket
# 2. Create folder "logos"
# 3. Upload aurum-brain-logo.svg
```

## Step 3: Configure CORS (if needed)

In Supabase Dashboard → Storage → Settings:

```json
{
  "allowedOrigins": ["https://your-domain.com"],
  "allowedMethods": ["GET", "POST", "PUT", "DELETE"],
  "allowedHeaders": ["*"],
  "exposedHeaders": ["*"],
  "maxAge": 86400
}
```

## Step 4: Environment Variables

Update your production `.env`:

```env
# Frontend
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key

# Backend
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
```

## Step 5: Update Image References

### Frontend Changes Made:
1. ✅ User avatars now use `AvatarCDNImage`
2. ✅ Charts use optimized components
3. ✅ Logo uses CDN path

### Migration Checklist:
- [ ] Upload existing user avatars to `avatars` bucket
- [ ] Upload product images to `images` bucket
- [ ] Upload documents to `documents` bucket
- [ ] Update any hardcoded image paths

## Step 6: Performance Monitoring

### Check CDN Performance:
```sql
-- Recent uploads
SELECT 
  bucket_id,
  name,
  created_at,
  metadata->>'size' as size,
  metadata->>'mimetype' as type
FROM storage.objects
WHERE created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;

-- Storage usage by user
SELECT * FROM get_user_storage_usage(auth.uid());
```

### Monitor Cache Hit Rates:
1. Use browser DevTools Network tab
2. Check for `cf-cache-status: HIT` headers
3. Monitor load times for images

## Step 7: Optional Cloudflare Integration

For enhanced CDN performance:

1. **Add Custom Domain**
   ```
   storage.yourdomain.com → your-project.supabase.co
   ```

2. **Cloudflare Page Rules**
   ```
   URL: storage.yourdomain.com/storage/v1/object/public/*
   Cache Level: Cache Everything
   Edge Cache TTL: 1 month
   ```

3. **Update Frontend URLs**
   ```javascript
   const CDN_BASE = process.env.REACT_APP_CDN_URL || 
     `${process.env.REACT_APP_SUPABASE_URL}/storage/v1/object/public`;
   ```

## Step 8: Image Optimization Best Practices

### Upload Processing:
```javascript
// Resize before upload
const resizeImage = async (file, maxWidth = 1600) => {
  // Implementation in image_processor.py
};

// Generate thumbnails
const generateThumbnail = async (file) => {
  // Create 200x200 thumbnail
};
```

### Responsive Images:
```jsx
<ResponsiveCDNImage
  bucket="images"
  path="hero.jpg"
  sizes="(max-width: 640px) 100vw, 50vw"
  priority={true}
/>
```

## Step 9: Cleanup and Maintenance

### Schedule Regular Cleanup:
```sql
-- Run monthly to clean temp files
SELECT cleanup_old_temp_uploads();
```

### Monitor Storage Growth:
```sql
-- Storage trend analysis
SELECT 
  DATE_TRUNC('day', created_at) as date,
  COUNT(*) as uploads,
  ROUND(SUM((metadata->>'size')::numeric) / 1048576, 2) as mb_added
FROM storage.objects
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY date DESC;
```

## Step 10: Testing Checklist

- [ ] Upload new avatar - verify CDN URL
- [ ] Upload image - check transformations work
- [ ] Test WebP conversion
- [ ] Verify responsive images load correctly
- [ ] Check browser caching works
- [ ] Test error handling (missing images)
- [ ] Verify private documents are secure

## Troubleshooting

### Issue: Images not loading
- Check bucket is public
- Verify CORS settings
- Check file path structure

### Issue: Slow loading
- Enable WebP format
- Use appropriate image sizes
- Check CDN cache headers

### Issue: Upload failures
- Check file size limits
- Verify mime types allowed
- Check user authentication

## Performance Metrics

After implementation, expect:
- 40-60% faster image loading
- 25-35% bandwidth reduction (WebP)
- Better SEO (faster page loads)
- Improved user experience

## Next Steps

1. Monitor performance for 1 week
2. Adjust cache durations if needed
3. Consider image lazy loading for below-fold content
4. Implement image preloading for critical assets