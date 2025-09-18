import { Heart, Target, FolderKanban, Calendar } from 'lucide-react';
import HierarchyCard from '../shared/HierarchyCard';
import { useAppStore } from '../../stores/basicAppStore';

// Example component showing the enhanced hierarchy card structure
export default function HierarchyCardExample() {
  const { navigateToPillar, navigateToArea, navigateToProject } = useAppStore();

  // Example Health & Wellness pillar data matching your image
  const healthPillarData = {
    id: 'health-wellness',
    name: 'Health & Wellness',
    description: 'Physical and mental well-being foundation',
    healthScore: 85,
    color: '#22C55E',
    subItems: [
      {
        id: 'nutrition',
        name: 'Nutrition',
        healthScore: 77,
        onClick: () => navigateToArea('nutrition', 'Nutrition')
      },
      {
        id: 'mental-health',
        name: 'Mental Health',
        healthScore: 76,
        onClick: () => navigateToArea('mental-health', 'Mental Health')
      },
      {
        id: 'sleep-recovery',
        name: 'Sleep & Recovery',
        healthScore: 96,
        onClick: () => navigateToArea('sleep-recovery', 'Sleep & Recovery')
      }
    ]
  };

  const exampleAreaData = {
    id: 'fitness-exercise',
    name: 'Fitness & Exercise',
    description: 'Physical activity and strength building',
    healthScore: 82,
    color: '#3B82F6',
    subItems: [
      {
        id: 'strength-training',
        name: 'Strength Training',
        progress: 85,
        onClick: () => navigateToProject('strength-training', 'Strength Training')
      },
      {
        id: 'cardio-routine',
        name: 'Cardio Routine',
        progress: 78,
        onClick: () => navigateToProject('cardio-routine', 'Cardio Routine')
      },
      {
        id: 'flexibility',
        name: 'Flexibility & Mobility',
        progress: 91,
        onClick: () => navigateToProject('flexibility', 'Flexibility & Mobility')
      }
    ]
  };

  return (
    <div className="space-y-8 p-6">
      <div>
        <h2 className="text-2xl font-bold text-white mb-4">Enhanced Hierarchy Cards</h2>
        <p className="text-[#B8BCC8] mb-6">
          Cards now follow the structure from your design with drill-down navigation and clickable sub-items.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pillar Example - matches your Health & Wellness card */}
        <HierarchyCard
          level="pillar"
          title={healthPillarData.name}
          description={healthPillarData.description}
          healthScore={healthPillarData.healthScore}
          icon={<Heart className="w-6 h-6" />}
          color={healthPillarData.color}
          iconBgColor={healthPillarData.color}
          metrics={[
            {
              label: 'Projects',
              value: 9,
              icon: <FolderKanban className="w-4 h-4" />,
              color: '#F4D03F',
            },
            {
              label: 'Completed',
              value: 8,
              icon: <Target className="w-4 h-4" />,
              color: '#10B981',
            },
            {
              label: 'Total Tasks',
              value: 37,
              icon: <Calendar className="w-4 h-4" />,
              color: '#B8BCC8',
            },
          ]}
          subItems={healthPillarData.subItems}
          onClick={() => navigateToPillar(healthPillarData.id, healthPillarData.name)}
          onEdit={() => console.log('Edit pillar')}
          onDelete={() => console.log('Delete pillar')}
        />

        {/* Area Example */}
        <HierarchyCard
          level="area"
          title={exampleAreaData.name}
          description={exampleAreaData.description}
          healthScore={exampleAreaData.healthScore}
          icon={<Target className="w-6 h-6" />}
          color={exampleAreaData.color}
          iconBgColor={exampleAreaData.color}
          badge={{
            text: 'Health & Wellness',
            variant: 'outline'
          }}
          metrics={[
            {
              label: 'Projects',
              value: 3,
              icon: <FolderKanban className="w-4 h-4" />,
              color: '#3B82F6',
            },
            {
              label: 'Tasks',
              value: 12,
              icon: <Calendar className="w-4 h-4" />,
              color: '#10B981',
            },
          ]}
          subItems={exampleAreaData.subItems}
          onClick={() => navigateToArea(exampleAreaData.id, exampleAreaData.name)}
          onEdit={() => console.log('Edit area')}
          onDelete={() => console.log('Delete area')}
        />
      </div>

      <div className="glassmorphism-panel p-6 rounded-lg">
        <h3 className="text-lg font-semibold text-white mb-3">Key Features</h3>
        <ul className="space-y-2 text-[#B8BCC8]">
          <li className="flex items-start space-x-2">
            <div className="w-2 h-2 bg-[#F4D03F] rounded-full mt-2 flex-shrink-0"></div>
            <span><strong>Main Card Click:</strong> Drills down to show only the next layer items that relate to that card</span>
          </li>
          <li className="flex items-start space-x-2">
            <div className="w-2 h-2 bg-[#F4D03F] rounded-full mt-2 flex-shrink-0"></div>
            <span><strong>Sub-item Click:</strong> Navigates directly to that sub-item's detail view and shows its sub-items</span>
          </li>
          <li className="flex items-start space-x-2">
            <div className="w-2 h-2 bg-[#F4D03F] rounded-full mt-2 flex-shrink-0"></div>
            <span><strong>Edit Ellipsis:</strong> Actions dropdown for edit, duplicate, and delete operations</span>
          </li>
          <li className="flex items-start space-x-2">
            <div className="w-2 h-2 bg-[#F4D03F] rounded-full mt-2 flex-shrink-0"></div>
            <span><strong>Visual Progress:</strong> Progress bars and percentages show completion status</span>
          </li>
          <li className="flex items-start space-x-2">
            <div className="w-2 h-2 bg-[#F4D03F] rounded-full mt-2 flex-shrink-0"></div>
            <span><strong>Metrics Display:</strong> Shows relevant statistics like project count and completion</span>
          </li>
        </ul>
      </div>
    </div>
  );
}