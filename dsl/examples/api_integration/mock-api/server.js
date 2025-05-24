/**
 * Mock API Server for Taskinity API Integration Examples
 */
const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');

// Create Express app
const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(morgan('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Data directory
const dataDir = path.join(__dirname, 'data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

// Weather API endpoint
app.get('/api/weather', (req, res) => {
  const { q, lat, lon } = req.query;
  let location = 'Unknown';
  
  if (q) {
    location = q;
  } else if (lat && lon) {
    location = `${lat},${lon}`;
  }
  
  console.log(`Weather request for location: ${location}`);
  
  // Generate mock weather data
  const now = Math.floor(Date.now() / 1000);
  const temp = 15 + Math.random() * 15; // 15-30°C
  const weather = ['Clear', 'Clouds', 'Rain', 'Thunderstorm', 'Drizzle', 'Snow', 'Mist'];
  const weatherIndex = Math.floor(Math.random() * weather.length);
  
  const descriptions = {
    'Clear': 'clear sky',
    'Clouds': 'few clouds',
    'Rain': 'light rain',
    'Thunderstorm': 'thunderstorm',
    'Drizzle': 'light drizzle',
    'Snow': 'light snow',
    'Mist': 'mist'
  };
  
  // Parse location
  let city = 'Warsaw';
  let country = 'PL';
  
  if (q) {
    const parts = q.split(',');
    city = parts[0];
    if (parts.length > 1) {
      country = parts[1];
    }
  }
  
  const response = {
    coord: {
      lon: lon || 21.0118,
      lat: lat || 52.2298
    },
    weather: [
      {
        id: 800 + weatherIndex,
        main: weather[weatherIndex],
        description: descriptions[weather[weatherIndex]],
        icon: '01d'
      }
    ],
    base: 'stations',
    main: {
      temp: temp,
      feels_like: temp - 2,
      temp_min: temp - 5,
      temp_max: temp + 5,
      pressure: 1013,
      humidity: 50 + Math.floor(Math.random() * 30)
    },
    visibility: 10000,
    wind: {
      speed: Math.random() * 10,
      deg: Math.floor(Math.random() * 360)
    },
    clouds: {
      all: Math.floor(Math.random() * 100)
    },
    dt: now,
    sys: {
      type: 2,
      id: 2000,
      country: country,
      sunrise: now - 3600,
      sunset: now + 3600
    },
    timezone: 7200,
    id: 756135,
    name: city,
    cod: 200
  };
  
  // Simulate network delay
  setTimeout(() => {
    res.status(200).json(response);
  }, 500);
});

// GitHub API endpoint
app.get('/api/github/users/:username', (req, res) => {
  const { username } = req.params;
  
  console.log(`GitHub user request for: ${username}`);
  
  const response = {
    login: username,
    id: 12345678,
    node_id: 'MDQ6VXNlcjEyMzQ1Njc4',
    avatar_url: 'https://avatars.githubusercontent.com/u/12345678?v=4',
    gravatar_id: '',
    url: `https://api.github.com/users/${username}`,
    html_url: `https://github.com/${username}`,
    followers_url: `https://api.github.com/users/${username}/followers`,
    following_url: `https://api.github.com/users/${username}/following{/other_user}`,
    gists_url: `https://api.github.com/users/${username}/gists{/gist_id}`,
    starred_url: `https://api.github.com/users/${username}/starred{/owner}{/repo}`,
    subscriptions_url: `https://api.github.com/users/${username}/subscriptions`,
    organizations_url: `https://api.github.com/users/${username}/orgs`,
    repos_url: `https://api.github.com/users/${username}/repos`,
    events_url: `https://api.github.com/users/${username}/events{/privacy}`,
    received_events_url: `https://api.github.com/users/${username}/received_events`,
    type: 'User',
    site_admin: false,
    name: `${username.charAt(0).toUpperCase() + username.slice(1)} User`,
    company: 'Taskinity',
    blog: `https://${username}.dev`,
    location: 'Warsaw, Poland',
    email: null,
    hireable: null,
    bio: 'Software developer and Taskinity enthusiast',
    twitter_username: username,
    public_repos: 20,
    public_gists: 5,
    followers: 100,
    following: 50,
    created_at: '2020-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z'
  };
  
  // Simulate network delay
  setTimeout(() => {
    res.status(200).json(response);
  }, 500);
});

// GitHub repos endpoint
app.get('/api/github/users/:username/repos', (req, res) => {
  const { username } = req.params;
  
  console.log(`GitHub repos request for user: ${username}`);
  
  const repos = [];
  const repoCount = 5 + Math.floor(Math.random() * 5); // 5-10 repos
  
  for (let i = 1; i <= repoCount; i++) {
    const repoName = `${username}-project-${i}`;
    repos.push({
      id: 100000 + i,
      node_id: `MDEwOlJlcG9zaXRvcnkxMDAwMDAke i}`,
      name: repoName,
      full_name: `${username}/${repoName}`,
      private: false,
      owner: {
        login: username,
        id: 12345678,
        avatar_url: 'https://avatars.githubusercontent.com/u/12345678?v=4',
        url: `https://api.github.com/users/${username}`
      },
      html_url: `https://github.com/${username}/${repoName}`,
      description: `A sample project ${i} by ${username}`,
      fork: false,
      url: `https://api.github.com/repos/${username}/${repoName}`,
      created_at: '2022-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z',
      pushed_at: '2023-01-01T00:00:00Z',
      homepage: null,
      size: 1000 * i,
      stargazers_count: 10 * i,
      watchers_count: 10 * i,
      language: ['JavaScript', 'Python', 'Java', 'Go', 'Ruby'][i % 5],
      forks_count: 5 * i,
      open_issues_count: i,
      license: {
        key: 'mit',
        name: 'MIT License',
        url: 'https://api.github.com/licenses/mit'
      },
      topics: ['taskinity', 'api', 'example', `topic-${i}`],
      visibility: 'public',
      default_branch: 'main'
    });
  }
  
  // Simulate network delay
  setTimeout(() => {
    res.status(200).json(repos);
  }, 700);
});

// REST API endpoints
app.get('/api/posts', (req, res) => {
  const posts = [];
  const postCount = 10;
  
  for (let i = 1; i <= postCount; i++) {
    posts.push({
      id: i,
      title: `Post ${i}`,
      body: `This is the body of post ${i}. It contains some sample text for the Taskinity API integration example.`,
      userId: (i % 5) + 1
    });
  }
  
  res.status(200).json(posts);
});

app.get('/api/posts/:id', (req, res) => {
  const { id } = req.params;
  
  const post = {
    id: parseInt(id),
    title: `Post ${id}`,
    body: `This is the body of post ${id}. It contains some sample text for the Taskinity API integration example.`,
    userId: (parseInt(id) % 5) + 1
  };
  
  res.status(200).json(post);
});

app.get('/api/users', (req, res) => {
  const users = [];
  const userCount = 5;
  
  for (let i = 1; i <= userCount; i++) {
    users.push({
      id: i,
      name: `User ${i}`,
      username: `user${i}`,
      email: `user${i}@example.com`,
      address: {
        street: `Street ${i}`,
        suite: `Suite ${i}`,
        city: `City ${i}`,
        zipcode: `0000${i}`,
        geo: {
          lat: `${i}.0000`,
          lng: `${i}.0000`
        }
      },
      phone: `123-456-789${i}`,
      website: `user${i}.example.com`,
      company: {
        name: `Company ${i}`,
        catchPhrase: `Catchphrase ${i}`,
        bs: `BS ${i}`
      }
    });
  }
  
  res.status(200).json(users);
});

// Error handling
app.use((req, res, next) => {
  res.status(404).json({ error: 'Not Found' });
});

app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal Server Error' });
});

// Start server
app.listen(port, () => {
  console.log(`Mock API server running at http://localhost:${port}`);
});
