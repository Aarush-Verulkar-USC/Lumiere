# XAI Movie Recommender - React Frontend

Modern, responsive frontend built with React, TypeScript, and Tailwind CSS.

## 🚀 Features

- **Modern UI/UX**: Clean, responsive design with smooth animations
- **TypeScript**: Full type safety for robust development
- **Tailwind CSS**: Utility-first styling with custom theme
- **Real-time Status**: Live API health monitoring
- **Error Handling**: Graceful error states with helpful messages
- **Responsive**: Works beautifully on all screen sizes
- **Fast**: Vite for lightning-fast development and builds

## 📋 Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- FastAPI backend running on http://localhost:8000

## 🛠️ Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` if your backend runs on a different URL:

```env
VITE_API_URL=http://localhost:8000
```

### 3. Start Development Server

```bash
npm run dev
```

The app will open at `http://localhost:3000`

## 📦 Build for Production

```bash
npm run build
```

Built files will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## 🎨 Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Header.tsx       # App header
│   │   ├── RecommendationCard.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── ErrorAlert.tsx
│   ├── services/            # API services
│   │   └── api.ts           # FastAPI client
│   ├── types/               # TypeScript types
│   │   └── index.ts
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles + Tailwind
├── public/                  # Static assets
├── index.html               # HTML template
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## 🎯 Usage

### Getting Recommendations

1. **Enter User ID**: Type a user ID (1-610)
2. **Select Count**: Use the slider to choose how many recommendations (1-10)
3. **Click "Get Recommendations"**: The app will fetch and display results

### System Status

The status bar shows:
- 🟢 **System Online**: Backend is healthy
- ✅ **Model**: Node2Vec model is loaded
- ✅ **Database**: Neo4j is connected

### Recommendation Cards

Each card shows:
- **Movie Title**: The recommended movie
- **Match Percentage**: Similarity score as percentage
- **Star Rating**: Visual representation (1-5 stars)
- **Explanation**: Why this movie was recommended
- **Technical Details**: Expandable section with similarity score and movie ID

## 🔧 Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Code Style

- **TypeScript**: Strict mode enabled
- **ESLint**: Configured for React and TypeScript
- **Prettier**: (optional) Add `.prettierrc` if desired

### Adding New Components

1. Create component in `src/components/`
2. Use TypeScript with proper typing
3. Import and use Tailwind classes
4. Export default component

Example:

```typescript
import React from 'react';

interface MyComponentProps {
  title: string;
}

const MyComponent: React.FC<MyComponentProps> = ({ title }) => {
  return (
    <div className="card">
      <h2 className="text-xl font-bold">{title}</h2>
    </div>
  );
};

export default MyComponent;
```

## 🎨 Styling

### Tailwind Classes

Custom classes defined in `index.css`:

- `.card` - White card with shadow
- `.btn-primary` - Primary gradient button
- `.btn-secondary` - Secondary gray button
- `.input-field` - Styled input field
- `.badge-*` - Colored badges for node types

### Theme Colors

Primary red gradient:
- `primary-500`: #ef4444
- `primary-600`: #dc2626
- `primary-700`: #b91c1c

Use in HTML:

```html
<button className="btn-primary">Click Me</button>
<div className="bg-primary-500 text-white p-4">Content</div>
```

### Custom Animations

- `animate-fade-in` - Fade in animation
- `animate-slide-up` - Slide up animation
- `animate-shimmer` - Loading shimmer effect

## 🔌 API Integration

The app communicates with the FastAPI backend via `src/services/api.ts`.

### API Methods

```typescript
import apiService from './services/api';

// Get recommendations
const recommendations = await apiService.getRecommendations(userId, count);

// Check health
const health = await apiService.getHealth();

// Get user's rated movies
const rated = await apiService.getUserRatedMovies(userId, limit);
```

### Error Handling

All API calls automatically handle errors and throw meaningful messages.

## 📱 Responsive Design

Breakpoints:
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

The layout adapts:
- Single column on mobile
- Two-column grid on desktop
- Collapsible navigation on mobile

## 🚀 Deployment

### Deploy to Vercel

```bash
npm install -g vercel
vercel
```

### Deploy to Netlify

```bash
npm run build
netlify deploy --prod --dir=dist
```

### Deploy to GitHub Pages

Add to `package.json`:

```json
{
  "homepage": "https://username.github.io/repo-name",
  "scripts": {
    "predeploy": "npm run build",
    "deploy": "gh-pages -d dist"
  }
}
```

```bash
npm install --save-dev gh-pages
npm run deploy
```

### Environment Variables

For production, set `VITE_API_URL` to your deployed backend URL.

## 🐛 Troubleshooting

### "Cannot connect to server"

**Cause**: Backend not running or wrong URL

**Solution**:
1. Start backend: `python main.py`
2. Check backend URL in `.env`
3. Verify backend is on http://localhost:8000

### "System Offline"

**Cause**: Health check failed

**Solution**:
1. Ensure Neo4j is running
2. Ensure Node2Vec model is trained
3. Check backend logs for errors

### Build Errors

**Cause**: Type errors or missing dependencies

**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Port Already in Use

**Cause**: Port 3000 is occupied

**Solution**:
```bash
# Use different port
npm run dev -- --port 3001
```

## 🔒 Security

- **No API Keys in Frontend**: All sensitive data stays in backend
- **CORS**: Backend must allow frontend origin
- **Input Validation**: User ID validated before API calls
- **Error Messages**: Don't expose sensitive information

## 📝 License

Same as main project.

## 🤝 Contributing

1. Create a feature branch
2. Make changes with proper TypeScript types
3. Test thoroughly
4. Submit pull request

---

**Built with ❤️ using React, TypeScript, and Tailwind CSS**
