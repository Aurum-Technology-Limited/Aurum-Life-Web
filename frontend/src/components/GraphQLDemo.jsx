/**
 * GraphQL Demo Component
 * Shows the benefits of GraphQL over REST
 */

import React, { useState } from 'react';
import { useQuery } from '@apollo/client';
import { gql } from '@apollo/client';
import { BarChart3, Zap, Database, TrendingDown } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';

// Example: Fetching dashboard data with GraphQL vs REST

// GraphQL Query - Get exactly what we need in one request
const GRAPHQL_DASHBOARD_QUERY = gql`
  query GetDashboardOptimized {
    dashboard {
      userStats {
        taskStats {
          total
          completed
          completionRate
        }
        totalPoints
        currentStreak
      }
      recentTasks(limit: 5) {
        id
        name
        priority
        dueDate
      }
      upcomingDeadlines(limit: 3) {
        id
        name
        dueDate
        project {
          name
        }
      }
    }
  }
`;

const GraphQLDemo = () => {
  const [showComparison, setShowComparison] = useState(true);
  
  // GraphQL Query
  const { data: graphqlData, loading: graphqlLoading } = useQuery(GRAPHQL_DASHBOARD_QUERY);

  // Simulated REST calls (what would happen with REST)
  const restApiCalls = [
    'GET /api/user/stats',
    'GET /api/tasks?limit=5&sort=created_at',
    'GET /api/tasks?has_due_date=true&completed=false&limit=3',
    'GET /api/projects?ids=1,2,3', // N+1 problem for project names
  ];

  const benefits = [
    {
      title: 'Single Request',
      graphql: '1 network request',
      rest: '4+ network requests',
      improvement: '75% fewer requests',
      icon: <Zap className="h-5 w-5 text-yellow-400" />,
    },
    {
      title: 'Data Transfer',
      graphql: '~2KB (exact fields)',
      rest: '~15KB (over-fetching)',
      improvement: '87% less data',
      icon: <TrendingDown className="h-5 w-5 text-green-400" />,
    },
    {
      title: 'Response Time',
      graphql: '~150ms',
      rest: '~600ms (waterfall)',
      improvement: '4x faster',
      icon: <BarChart3 className="h-5 w-5 text-blue-400" />,
    },
    {
      title: 'Caching',
      graphql: 'Automatic & granular',
      rest: 'Manual & endpoint-based',
      improvement: 'Smarter caching',
      icon: <Database className="h-5 w-5 text-purple-400" />,
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white mb-2">GraphQL vs REST API</h2>
        <p className="text-gray-400">See how GraphQL improves data fetching efficiency</p>
      </div>

      <Tabs defaultValue="comparison" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="comparison">Comparison</TabsTrigger>
          <TabsTrigger value="graphql">GraphQL Example</TabsTrigger>
          <TabsTrigger value="rest">REST Example</TabsTrigger>
        </TabsList>

        <TabsContent value="comparison" className="space-y-4">
          {/* Performance Benefits */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {benefits.map((benefit, index) => (
              <Card key={index} className="bg-gray-800 border-gray-700">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    {benefit.icon}
                    <Badge variant="success" className="text-xs">
                      {benefit.improvement}
                    </Badge>
                  </div>
                  <CardTitle className="text-sm mt-2">{benefit.title}</CardTitle>
                </CardHeader>
                <CardContent className="text-xs space-y-1">
                  <div>
                    <span className="text-green-400 font-medium">GraphQL:</span>{' '}
                    <span className="text-gray-400">{benefit.graphql}</span>
                  </div>
                  <div>
                    <span className="text-red-400 font-medium">REST:</span>{' '}
                    <span className="text-gray-400">{benefit.rest}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Query Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-green-400">GraphQL Approach</CardTitle>
                <CardDescription>One query, exact data</CardDescription>
              </CardHeader>
              <CardContent>
                <pre className="text-xs bg-gray-900 p-3 rounded overflow-x-auto">
{`query GetDashboard {
  dashboard {
    userStats {
      taskStats { total, completed }
      totalPoints
    }
    recentTasks(limit: 5) {
      id, name, priority
    }
    upcomingDeadlines {
      name, dueDate
      project { name }
    }
  }
}`}
                </pre>
                <div className="mt-3 text-sm text-gray-400">
                  ✅ Single request<br/>
                  ✅ No over-fetching<br/>
                  ✅ Nested data in one call
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-red-400">REST Approach</CardTitle>
                <CardDescription>Multiple endpoints, extra data</CardDescription>
              </CardHeader>
              <CardContent>
                <pre className="text-xs bg-gray-900 p-3 rounded overflow-x-auto">
{restApiCalls.map(call => `${call}\n`).join('')}
                </pre>
                <div className="mt-3 text-sm text-gray-400">
                  ❌ Multiple requests<br/>
                  ❌ Over-fetching data<br/>
                  ❌ N+1 query problem<br/>
                  ❌ Waterfall loading
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="graphql" className="space-y-4">
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle>Live GraphQL Data</CardTitle>
              <CardDescription>Fetched with Apollo Client</CardDescription>
            </CardHeader>
            <CardContent>
              {graphqlLoading ? (
                <div className="text-gray-400">Loading...</div>
              ) : (
                <div className="space-y-4">
                  {/* User Stats */}
                  <div>
                    <h4 className="text-sm font-medium text-white mb-2">User Stats</h4>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div className="bg-gray-900 p-3 rounded">
                        <div className="text-gray-400">Tasks</div>
                        <div className="text-xl font-bold text-white">
                          {graphqlData?.dashboard?.userStats?.taskStats?.completed} / 
                          {graphqlData?.dashboard?.userStats?.taskStats?.total}
                        </div>
                      </div>
                      <div className="bg-gray-900 p-3 rounded">
                        <div className="text-gray-400">Points</div>
                        <div className="text-xl font-bold text-yellow-400">
                          {graphqlData?.dashboard?.userStats?.totalPoints || 0}
                        </div>
                      </div>
                      <div className="bg-gray-900 p-3 rounded">
                        <div className="text-gray-400">Streak</div>
                        <div className="text-xl font-bold text-green-400">
                          {graphqlData?.dashboard?.userStats?.currentStreak || 0} days
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Recent Tasks */}
                  <div>
                    <h4 className="text-sm font-medium text-white mb-2">Recent Tasks</h4>
                    <div className="space-y-2">
                      {graphqlData?.dashboard?.recentTasks?.map(task => (
                        <div key={task.id} className="flex items-center justify-between bg-gray-900 p-2 rounded">
                          <span className="text-sm">{task.name}</span>
                          <Badge variant={task.priority === 'HIGH' ? 'destructive' : 'secondary'}>
                            {task.priority}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="rest" className="space-y-4">
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle>REST API Calls</CardTitle>
              <CardDescription>Multiple requests with over-fetching</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {restApiCalls.map((call, index) => (
                <div key={index} className="bg-gray-900 p-3 rounded">
                  <div className="flex items-center justify-between mb-2">
                    <code className="text-sm text-green-400">{call}</code>
                    <Badge variant="outline" className="text-xs">
                      ~150ms
                    </Badge>
                  </div>
                  <div className="text-xs text-gray-500">
                    Returns entire objects with 20+ fields when we only need 3-4
                  </div>
                </div>
              ))}
              
              <div className="mt-4 p-3 bg-red-900/20 border border-red-800 rounded">
                <div className="text-sm text-red-400 font-medium">Issues:</div>
                <ul className="text-xs text-gray-400 mt-1 space-y-1">
                  <li>• Total time: ~600ms (waterfall)</li>
                  <li>• Data transferred: ~15KB (vs 2KB with GraphQL)</li>
                  <li>• 4 separate requests to maintain</li>
                  <li>• Frontend needs to combine data from multiple sources</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Migration Guide */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle>Ready to Use GraphQL?</CardTitle>
          <CardDescription>GraphQL endpoint is available at /graphql</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="text-sm text-gray-400">
            <p>1. GraphQL Playground available at: <code className="text-green-400">{window.location.origin}/graphql</code></p>
            <p>2. Use the custom hooks: <code className="text-green-400">useTasks(), useProjects(), etc.</code></p>
            <p>3. Automatic caching and optimistic updates included</p>
            <p>4. REST endpoints remain available during migration</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default GraphQLDemo;