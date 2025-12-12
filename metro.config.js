const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Allow backend service name resolution
config.resolver.alias = {
  ...config.resolver.alias,
  'backend': 'http://backend:8001'
};

// Allow network requests to backend
config.server = {
  ...config.server,
  enhanceMiddleware: (middleware) => {
    return (req, res, next) => {
      // Allow all CORS requests
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
      
      if (req.method === 'OPTIONS') {
        res.statusCode = 200;
        res.end();
        return;
      }
      
      return middleware(req, res, next);
    };
  },
};

module.exports = config;