from datetime import datetime, time, timedelta
from django.utils import timezone
from core.models import SmartActivity, UserTimetable, Schedule

class SmartScheduler:
    def __init__(self, user):
        self.user = user
        self.profile = user.profile
    
    def initialize_gentleman_routine(self):
        """Create the initial gentleman routine with emojis"""
        base_activities = [
            # Fixed morning routine
            {
                'title': 'Wake Up & Grooming',
                'category': 'morning_routine',
                'start_time': time(6, 0),
                'duration_minutes': 30,
                'priority_level': 1,  # Fixed
                'is_flexible': False,
                'description': 'Morning wake up, grooming, and preparation'
            },
            {
                'title': 'Morning Workout',
                'category': 'fitness',
                'start_time': time(6, 30),
                'duration_minutes': 45,
                'priority_level': 2,
                'is_flexible': True,
                'description': 'Physical exercise and fitness routine'
            },
            {
                'title': 'Breakfast',
                'category': 'meal',
                'start_time': time(7, 15),
                'duration_minutes': 30,
                'priority_level': 2,
                'is_flexible': True,
                'description': 'Morning meal and nutrition'
            },
            # Academic blocks (will be adjusted around timetable)
            {
                'title': 'Morning Study Block',
                'category': 'academic',
                'start_time': time(8, 0),
                'duration_minutes': 120,
                'priority_level': 3,
                'is_flexible': True,
                'description': 'Focused study session'
            },
            {
                'title': 'Lunch Break',
                'category': 'meal',
                'start_time': time(12, 0),
                'duration_minutes': 45,
                'priority_level': 2,
                'is_flexible': True,
                'description': 'Lunch and rest period'
            },
            {
                'title': 'Afternoon Study',
                'category': 'academic',
                'start_time': time(13, 0),
                'duration_minutes': 180,
                'priority_level': 3,
                'is_flexible': True,
                'description': 'Continued academic work'
            },
            # Personal development
            {
                'title': 'Girlfriend Time',
                'category': 'social',
                'start_time': time(17, 15),
                'duration_minutes': 75,
                'priority_level': 2,
                'is_flexible': True,
                'description': 'Quality relationship time'
            },
            {
                'title': 'Self-Improvement',
                'category': 'personal',
                'start_time': time(18, 45),
                'duration_minutes': 75,
                'priority_level': 3,
                'is_flexible': True,
                'description': 'Reading, skills development, personal growth'
            },
            # Evening routine
            {
                'title': 'Dinner',
                'category': 'meal',
                'start_time': time(20, 15),
                'duration_minutes': 45,
                'priority_level': 2,
                'is_flexible': True,
                'description': 'Evening meal'
            },
            {
                'title': 'Reflection & Journaling',
                'category': 'reflection',
                'start_time': time(21, 15),
                'duration_minutes': 60,
                'priority_level': 3,
                'is_flexible': True,
                'description': 'Daily reflection, planning, journaling'
            },
            {
                'title': 'Wind Down & Sleep Prep',
                'category': 'rest',
                'start_time': time(22, 15),
                'duration_minutes': 75,
                'priority_level': 2,
                'is_flexible': False,
                'description': 'Relaxation and preparation for sleep'
            },
        ]
        
        created_count = 0
        for activity_data in base_activities:
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                # Calculate end time
                start_time = activity_data['start_time']
                duration = activity_data['duration_minutes']
                end_time = self._add_minutes_to_time(start_time, duration)
                
                SmartActivity.objects.create(
                    user=self.user,
                    day=day,
                    title=activity_data['title'],  # Title without emoji - display_title property will add it
                    category=activity_data['category'],
                    start_time=start_time,
                    end_time=end_time,
                    duration_minutes=duration,
                    priority_level=activity_data['priority_level'],
                    is_flexible=activity_data['is_flexible'],
                    description=activity_data['description'],
                    original_start_time=start_time
                )
                created_count += 1
        
        return created_count
    
    def _add_minutes_to_time(self, time_obj, minutes):
        """Add minutes to a time object"""
        dummy_date = datetime(2000, 1, 1)
        combined = datetime.combine(dummy_date, time_obj)
        new_time = combined + timedelta(minutes=minutes)
        return new_time.time()
    
    def adjust_schedule_for_timetable(self, day):
        """Adjust smart activities based on timetable for a specific day"""
        # Get timetable entries for the day
        timetable_entries = UserTimetable.objects.filter(
            user=self.user, 
            day=day, 
            is_active=True
        ).order_by('start_time')
        
        # Get smart activities for the day
        smart_activities = SmartActivity.objects.filter(
            user=self.user,
            day=day,
            is_active=True
        ).order_by('start_time')
        
        if not timetable_entries:
            # No timetable, reset to original times
            self._reset_to_original_times(smart_activities)
            return
        
        # Create time blocks for the day
        time_blocks = self._create_time_blocks(timetable_entries, smart_activities)
        
        # Adjust smart activities
        self._place_activities_in_gaps(time_blocks, smart_activities, day)
    
    def _create_time_blocks(self, timetable_entries, smart_activities):
        """Create occupied time blocks from timetable"""
        time_blocks = []
        
        # Add timetable blocks (fixed, cannot be moved)
        for entry in timetable_entries:
            time_blocks.append({
                'start': entry.start_time,
                'end': entry.end_time,
                'type': 'timetable',
                'activity': entry,
                'priority': 1  # Highest priority
            })
        
        # Add fixed smart activities (like wake up and sleep)
        for activity in smart_activities:
            if activity.priority_level == 1:  # Fixed activities
                time_blocks.append({
                    'start': activity.start_time,
                    'end': activity.end_time,
                    'type': 'fixed_smart',
                    'activity': activity,
                    'priority': 1
                })
        
        return sorted(time_blocks, key=lambda x: x['start'])
    
    def _place_activities_in_gaps(self, time_blocks, smart_activities, day):
        """Place flexible activities in available time gaps"""
        # Find all flexible activities
        flexible_activities = [
            activity for activity in smart_activities 
            if activity.is_flexible and activity.priority_level > 1
        ]
        
        # Sort by priority (lower number = higher priority)
        flexible_activities.sort(key=lambda x: x.priority_level)
        
        # Find time gaps between fixed blocks
        gaps = self._find_time_gaps(time_blocks)
        
        # Place activities in gaps
        for activity in flexible_activities:
            placed = False
            for gap in gaps:
                if self._can_fit_activity(activity, gap):
                    self._place_activity_in_gap(activity, gap)
                    placed = True
                    
                    # Update the gap (reduce available time)
                    gap['start'] = activity.end_time
                    gap['duration'] = self._time_difference_minutes(gap['start'], gap['end'])
                    break
            
            if not placed:
                # If no gap found, try to shorten and fit
                self._emergency_placement(activity, flexible_activities, gaps, day)
    
    def _find_time_gaps(self, time_blocks):
        """Find available time gaps between occupied blocks"""
        gaps = []
        day_start = time(6, 0)  # Wake up time
        day_end = time(23, 30)  # Sleep time
        
        # Sort time blocks by start time
        time_blocks.sort(key=lambda x: x['start'])
        
        # Check gap before first activity
        if time_blocks and time_blocks[0]['start'] > day_start:
            gaps.append({
                'start': day_start,
                'end': time_blocks[0]['start'],
                'duration': self._time_difference_minutes(day_start, time_blocks[0]['start'])
            })
        
        # Check gaps between activities
        for i in range(len(time_blocks) - 1):
            current_end = time_blocks[i]['end']
            next_start = time_blocks[i + 1]['start']
            
            if next_start > current_end:
                gap_duration = self._time_difference_minutes(current_end, next_start)
                if gap_duration >= 15:  # Minimum 15-minute gap
                    gaps.append({
                        'start': current_end,
                        'end': next_start,
                        'duration': gap_duration
                    })
        
        # Check gap after last activity
        if time_blocks and time_blocks[-1]['end'] < day_end:
            gaps.append({
                'start': time_blocks[-1]['end'],
                'end': day_end,
                'duration': self._time_difference_minutes(time_blocks[-1]['end'], day_end)
            })
        
        return sorted(gaps, key=lambda x: x['duration'], reverse=True)
    
    def _can_fit_activity(self, activity, gap):
        """Check if activity can fit in a time gap"""
        return gap['duration'] >= activity.duration_minutes
    
    def _place_activity_in_gap(self, activity, gap):
        """Place activity in a time gap"""
        activity.start_time = gap['start']
        activity.end_time = self._add_minutes_to_time(gap['start'], activity.duration_minutes)
        activity.adjustment_count += 1
        activity.last_adjusted = timezone.now()
        activity.save()
    
    def _emergency_placement(self, activity, all_activities, gaps, day):
        """Emergency placement when no suitable gap is found"""
        # Try to shorten the activity if possible
        if activity.duration_minutes > activity.min_duration_minutes:
            # Reduce duration to minimum and try again
            original_duration = activity.duration_minutes
            activity.duration_minutes = activity.min_duration_minutes
            
            for gap in gaps:
                if self._can_fit_activity(activity, gap):
                    self._place_activity_in_gap(activity, gap)
                    # Log that we shortened this activity
                    print(f"Shortened {activity.title} from {original_duration} to {activity.duration_minutes} minutes")
                    return
        
        # If still no placement, place at the end of the day
        last_gap = gaps[-1] if gaps else {'start': time(22, 0), 'end': time(23, 30)}
        self._place_activity_in_gap(activity, last_gap)
        print(f"Emergency placement for {activity.title} at {activity.start_time}")
    
    def _reset_to_original_times(self, smart_activities):
        """Reset activities to their original times when no timetable conflicts"""
        for activity in smart_activities:
            if activity.original_start_time and activity.start_time != activity.original_start_time:
                activity.start_time = activity.original_start_time
                activity.end_time = self._add_minutes_to_time(
                    activity.original_start_time, 
                    activity.duration_minutes
                )
                activity.save()
    
    def _time_difference_minutes(self, start_time, end_time):
        """Calculate time difference in minutes"""
        dummy_date = datetime(2000, 1, 1)
        start_dt = datetime.combine(dummy_date, start_time)
        end_dt = datetime.combine(dummy_date, end_time)
        return int((end_dt - start_dt).total_seconds() / 60)