# ruff: noqa
import sys
from fastmcp import FastMCP

mcp = FastMCP("Parenting MCP Server")

@mcp.tool()
def recommend_screen_time_limit(age: int) -> dict:
    """Calculates age-based screen time limits and provides structural guidelines.

    Args:
        age: The age of the child in years.

    Returns:
        dict containing the recommended daily limit in hours and parenting suggestions.
    """
    print(f"Executing recommend_screen_time_limit for age={age}", file=sys.stderr)
    
    if age < 2:
        limit = 0.0
        guideline = "No screen time recommended, except for high-quality video chatting under parental supervision."
        tips = ["Focus on interactive non-screen play", "Prioritize face-to-face communication"]
    elif age <= 5:
        limit = 1.0
        guideline = "Max 1 hour per day of high-quality educational programming."
        tips = ["Co-view programs with your child to help them understand", "Ensure screens don't replace sleep or physical play"]
    elif age <= 12:
        limit = 1.5
        guideline = "Max 1.5 hours per day of non-educational screen time."
        tips = ["Establish screen-free zones (e.g., bedrooms, dinnertime)", "Encourage physical activities and outdoor play"]
    else:
        limit = 2.0
        guideline = "Max 2.0 hours per day. Foster digital citizenship and balance."
        tips = ["Negotiate screen limits collaboratively", "Encourage media creation over passive media consumption"]
        
    return {
        "age": age,
        "recommended_daily_hours": limit,
        "guideline": guideline,
        "tips": tips
    }

@mcp.tool()
def suggest_discipline_strategy(age: int, behavior: str) -> dict:
    """Provides non-physical, moral-focused parenting discipline strategies based on child age and behavior.

    Args:
        age: The child's age in years.
        behavior: Description of the behavior (e.g., 'tantrum', 'lying', 'refusing chores').

    Returns:
        dict of age-specific strategies and the moral lesson.
    """
    print(f"Executing suggest_discipline_strategy for age={age}, behavior={behavior}", file=sys.stderr)
    
    behavior_lower = behavior.lower()
    
    if age <= 4:
        strategies = [
            "Positive Redirection: Redirect to a constructive activity or focus on another object.",
            "Brief Time-in/Cool-down: Sit with the child and help them calm down before addressing behavior.",
            "Clear and Simple Choices: Offer two acceptable options (e.g., 'Do you want to wear the red or blue shoes?')."
        ]
        moral = "Learning self-regulation and respecting simple boundaries."
    elif age <= 8:
        strategies = [
            "Logical Consequences: Directly tie the consequence to the behavior (e.g., 'If toys aren't put away, they go in timeout for 24 hours').",
            "Behavior Charts: Use positive reinforcement tokens for target actions.",
            "Praise Positive Opposite: Acknowledge the child when they behave correctly."
        ]
        moral = "Developing personal responsibility and understanding cause-and-effect."
    elif age <= 12:
        strategies = [
            "Problem-Solving Discussions: Sit together to discuss why the behavior happened and brainstorm solutions.",
            "Loss of Privileges: Temporarily revoke access to screens, playdates, or toys.",
            "Restitution: Perform a kind act or service to compensate if they hurt someone or broke something."
        ]
        moral = "Fostering empathy, respect, and constructive problem-solving."
    else:
        strategies = [
            "Collaborative Contracting: Create a written agreement detailing rules, privileges, and consequences.",
            "Privilege Review: Make certain privileges (e.g., car usage, phone access) contingent on responsible actions.",
            "Reflective Conversations: Discuss long-term consequences of behavior on relationships and personal growth."
        ]
        moral = "Developing autonomy, integrity, moral maturity, and mutual respect."

    return {
        "age": age,
        "behavior": behavior,
        "strategies": strategies,
        "moral_lesson": moral
    }

@mcp.tool()
def get_disability_resources(category: str) -> dict:
    """Provides directories and guidance for developmental disabilities, neurodiversity, or special needs.

    Args:
        category: One of 'autism', 'adhd', 'dyslexia', or 'general_disability'.

    Returns:
        dict containing resources, organizations, and support steps.
    """
    print(f"Executing get_disability_resources for category={category}", file=sys.stderr)
    
    cat = category.lower()
    
    if "autism" in cat:
        resources = [
            {"name": "Autism Speaks", "url": "https://www.autismspeaks.org", "description": "Resource directories, toolkits, and local support services."},
            {"name": "Autistic Self Advocacy Network (ASAN)", "url": "https://autisticadvocacy.org", "description": "Self-advocacy support and policy representation."},
            {"name": "IEP Guide for Autism", "url": "https://www.iidc.indiana.edu", "description": "Educational guide on drafting Autism-specific IEP goals."}
        ]
        tips = ["Leverage visual schedules", "Create quiet sensory-friendly zones"]
    elif "adhd" in cat:
        resources = [
            {"name": "CHADD", "url": "https://chadd.org", "description": "Children and Adults with Attention-Deficit/Hyperactivity Disorder support network."},
            {"name": "ADDitude Magazine", "url": "https://www.additudemag.com", "description": "Parenting strategies, school tips, and ADHD resources."},
            {"name": "Understood.org", "url": "https://www.understood.org", "description": "Tools for learning differences and executive functioning."}
        ]
        tips = ["Use structured routine checklists", "Break tasks into small, manageable chunks"]
    elif "dyslexia" in cat:
        resources = [
            {"name": "International Dyslexia Association", "url": "https://dyslexiaida.org", "description": "Information on reading intervention methods and structured literacy."},
            {"name": "Learning Disabilities Association of America", "url": "https://ldaamerica.org", "description": "Support resources for parents and special education advocates."}
        ]
        tips = ["Focus on multi-sensory reading tools", "Build confidence by celebrating non-reading strengths"]
    else:
        resources = [
            {"name": "Parent Training and Information Centers (PTI)", "url": "https://www.parentcenterhub.org", "description": "Local state-funded centers that assist parents with IEPs and disability rights."},
            {"name": "Wrightslaw", "url": "https://www.wrightslaw.com", "description": "Comprehensive resource on special education law and advocacy."}
        ]
        tips = ["Seek support early to secure accommodations", "Involve teachers and specialists in a collaborative team approach"]

    return {
        "category": category,
        "resources": resources,
        "accommodations_tips": tips
    }

@mcp.tool()
def fetch_mental_health_activities(emotion: str) -> dict:
    """Suggestions for emotional regulation, coping mechanisms, or mindfulness exercises.

    Args:
        emotion: The emotion or struggle (e.g., 'anxiety', 'stress', 'sadness', 'anger').

    Returns:
        dict of emotional activities and tips.
    """
    print(f"Executing fetch_mental_health_activities for emotion={emotion}", file=sys.stderr)
    
    emo = emotion.lower()
    
    if "anxiety" in emo or "worry" in emo:
        activities = [
            {"name": "Box Breathing", "steps": "Inhale for 4 seconds, hold for 4 seconds, exhale for 4 seconds, hold for 4 seconds. Repeat 4 times."},
            {"name": "Worry Jar", "steps": "Write down worries on slips of paper and place them in a physical jar to inspect or discuss later during designated 'worry time'."}
        ]
    elif "anger" in emo or "mad" in emo:
        activities = [
            {"name": "The Calm Down Corner", "steps": "A soft, quiet space equipped with pillows, stress balls, and drawing materials where children can voluntarily go to decompress."},
            {"name": "Ripping Paper / Squeezing Dough", "steps": "Allows safe physical release of anger tension without harming others."}
        ]
    else:
        activities = [
            {"name": "5-4-3-2-1 Grounding Method", "steps": "Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste."},
            {"name": "Emotion Journaling", "steps": "Encourage drawing or writing feelings to externalize internal stress."}
        ]
        
    return {
        "target_emotion": emotion,
        "suggested_activities": activities,
        "parenting_tip": "Focus on validating the child's emotion before trying to solve the problem."
    }

if __name__ == "__main__":
    mcp.run()
