import http from 'k6/http';
import { check, sleep } from 'k6';


export const options = {
  stages: [
    { duration: '10s', target: 10 },   
    { duration: '20s', target: 10 },   
    { duration: '10s', target: 50 },   
    { duration: '20s', target: 50 },  
    { duration: '10s', target: 0 },    
  ],
  thresholds: {
  
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

const TOKEN = __ENV.TOKEN;

export default function () {
  const res = http.get('http://localhost:8080/api/posts/feed/', {
    headers: { Authorization: `Bearer ${TOKEN}` },
  });

  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  sleep(1); 
}