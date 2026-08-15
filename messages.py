import random
from typing import Dict, List, Tuple

MOTIVATIONAL_QUOTES: List[Dict[str, str]] = [
    {"text": "The secret of getting ahead is getting started.", "author": "Mark Twain"},
    {"text": "It always seems impossible until it's done.", "author": "Nelson Mandela"},
    {"text": "Don't watch the clock; do what it does. Keep going.", "author": "Sam Levenson"},
    {"text": "Quality is not an act, it is a habit.", "author": "Aristotle"},
    {"text": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
    {"text": "Our greatest weakness lies in giving up. The most certain way to succeed is always to try just one more time.", "author": "Thomas A. Edison"},
    {"text": "Start where you are. Use what you have. Do what you can.", "author": "Arthur Ashe"},
    {"text": "Aim for the moon. If you miss, you may hit a star.", "author": "W. Clement Stone"},
    {"text": "Keep your eyes on the stars, and your feet on the ground.", "author": "Theodore Roosevelt"},
    {"text": "Either you run the day or the day runs you.", "author": "Jim Rohn"},
    {"text": "Act as if what you do makes a difference. It does.", "author": "William James"},
    {"text": "Success is not final, failure is not fatal: it is the courage to continue that counts.", "author": "Winston Churchill"},
    {"text": "Never bend your head. Always hold it high. Look the world straight in the eye.", "author": "Helen Keller"},
    {"text": "What you get by achieving your goals is not as important as what you become by achieving your goals.", "author": "Zig Ziglar"},
    {"text": "You miss 100% of the shots you don't take.", "author": "Wayne Gretzky"},
    {"text": "I failed my way to success.", "author": "Thomas Edison"},
    {"text": "Dream big and dare to fail.", "author": "Norman Vaughan"},
    {"text": "Courage is grace under pressure.", "author": "Ernest Hemingway"},
    {"text": "If you're going through hell, keep going.", "author": "Winston Churchill"},
    {"text": "It is during our darkest moments that we must focus to see the light.", "author": "Aristotle"},
    {"text": "Do one thing every day that scares you.", "author": "Eleanor Roosevelt"},
    {"text": "Well done is better than well said.", "author": "Benjamin Franklin"},
    {"text": "In the middle of every difficulty lies opportunity.", "author": "Albert Einstein"},
    {"text": "A champion is defined by how they recover when they fall.", "author": "Serena Williams"},
    {"text": "Happiness is not something readymade. It comes from your own actions.", "author": "Dalai Lama"},
    {"text": "You do not find the happy life. You make it.", "author": "Camilla Eyring Kimball"},
    {"text": "Troubles are often tools by which God fashions us for better things.", "author": "Henry Ward Beecher"},
    {"text": "Energy and persistence conquer all things.", "author": "Benjamin Franklin"},
    {"text": "Great minds discuss ideas; average minds discuss events; small minds discuss people.", "author": "Eleanor Roosevelt"},
    {"text": "Turn your wounds into wisdom.", "author": "Oprah Winfrey"},
    {"text": "We generate fears while we sit. We overcome them by action.", "author": "Dr. Henry Link"},
    {"text": "Whether you think you can or think you can't, you're right.", "author": "Henry Ford"},
    {"text": "Do what you can, with what you have, where you are.", "author": "Theodore Roosevelt"},
    {"text": "Today's accomplishments were yesterday's impossibilities.", "author": "Robert H. Schuller"},
    {"text": "You must be the change you wish to see in the world.", "author": "Mahatma Gandhi"},
    {"text": "The power of imagination makes us infinite.", "author": "John Muir"},
    {"text": "Make each day your masterpiece.", "author": "John Wooden"},
    {"text": "Light tomorrow with today.", "author": "Elizabeth Barrett Browning"},
    {"text": "The best way out is always through.", "author": "Robert Frost"},
    {"text": "If there is no struggle, there is no progress.", "author": "Frederick Douglass"},
    {"text": "Small deeds done are better than great deeds planned.", "author": "Peter Marshall"},
    {"text": "Doubt kills more dreams than failure ever will.", "author": "Suzy Kassem"},
    {"text": "Action is the foundational key to all success.", "author": "Pablo Picasso"},
    {"text": "You are never too old to set another goal or to dream a new dream.", "author": "C.S. Lewis"},
    {"text": "Everything you've ever wanted is on the other side of fear.", "author": "George Addair"},
    {"text": "Your time is limited, so don't waste it living someone else's life.", "author": "Steve Jobs"},
    {"text": "Hardships often prepare ordinary people for an extraordinary destiny.", "author": "C.S. Lewis"},
    {"text": "Build your own dreams, or someone else will hire you to build theirs.", "author": "Farrah Gray"},
    {"text": "Change your thoughts and you change your world.", "author": "Norman Vincent Peale"},
    {"text": "It is never too late to be what you might have been.", "author": "George Eliot"},
    {"text": "Stay hungry, stay foolish.", "author": "Steve Jobs"},
    {"text": "Whatever you are, be a good one.", "author": "Abraham Lincoln"},
    {"text": "Be so good they can't ignore you.", "author": "Steve Martin"},
    {"text": "There are no shortcuts to any place worth going.", "author": "Beverly Sills"},
    {"text": "You can manifest anything you put your mind to.", "author": "Unknown"},
    {"text": "Consistency is what transforms average into excellence.", "author": "Unknown"},
    {"text": "Do not let what you cannot do interfere with what you can do.", "author": "John Wooden"},
    {"text": "Opportunities don't happen. You create them.", "author": "Chris Grosser"},
    {"text": "Try not to become a man of success. Rather become a man of value.", "author": "Albert Einstein"},
    {"text": "Don't be afraid to give up the good to go for the great.", "author": "John D. Rockefeller"},
    {"text": "I find that the harder I work, the more luck I seem to have.", "author": "Thomas Jefferson"},
    {"text": "Success usually comes to those who are too busy to be looking for it.", "author": "Henry David Thoreau"},
    {"text": "There is no secret to success. It is the result of preparation, hard work, and learning from failure.", "author": "Colin Powell"},
    {"text": "Focus on being productive instead of busy.", "author": "Tim Ferriss"},
    {"text": "Small daily improvements over time lead to stunning results.", "author": "Robin Sharma"},
    {"text": "If you want to achieve greatness stop asking for permission.", "author": "Anonymous"},
    {"text": "Things work out best for those who make the best of how things work out.", "author": "John Wooden"},
    {"text": "To live a creative life, we must lose our fear of being wrong.", "author": "Joseph Chilton Pearce"},
    {"text": "If you are not willing to risk the usual you will have to settle for the ordinary.", "author": "Jim Rohn"},
    {"text": "Trust because you are willing to accept the risk, not because it's safe or certain.", "author": "Anonymous"},
    {"text": "All our dreams can come true if we have the courage to pursue them.", "author": "Walt Disney"},
    {"text": "Good things come to people who wait, but better things come to those who go out and get them.", "author": "Anonymous"},
    {"text": "If you do what you've always done, you'll get what you've always gotten.", "author": "Tony Robbins"},
    {"text": "Success is walking from failure to failure with no loss of enthusiasm.", "author": "Winston Churchill"},
    {"text": "Just when the caterpillar thought the world was ending, he turned into a butterfly.", "author": "Proverb"},
    {"text": "Successful entrepreneurs are givers and not takers of positive energy.", "author": "Anonymous"},
    {"text": "Whenever you see a successful person you only see the public glories, never the private sacrifices to reach them.", "author": "Vaibhav Shah"},
    {"text": "Opportunities multiply as they are seized.", "author": "Sun Tzu"},
    {"text": "If you don't design your own life plan, chances are you'll fall into someone else's plan.", "author": "Jim Rohn"},
    {"text": "Work hard in silence, let your success be your noise.", "author": "Frank Ocean"},
    {"text": "The difference between winning and losing is most often not quitting.", "author": "Walt Disney"},
    {"text": "I owe my success to having listened respectfully to the very best advice, and then going away and doing the exact opposite.", "author": "G.K. Chesterton"},
    {"text": "If you really look closely, most overnight successes took a long time.", "author": "Steve Jobs"},
    {"text": "The real test is not whether you avoid this failure, because you won't. It's whether you let it harden or shame you into inaction.", "author": "Barack Obama"},
    {"text": "Patience, persistence and perspiration make an unbeatable combination for success.", "author": "Napoleon Hill"},
    {"text": "There is only one way to avoid criticism: do nothing, say nothing, and be nothing.", "author": "Aristotle"},
    {"text": "Ask yourself if what you are doing today is getting you closer to where you want to be tomorrow.", "author": "Anonymous"},
    {"text": "Don't compare your beginning to someone else's middle.", "author": "Jon Acuff"},
    {"text": "The only limit to our realization of tomorrow will be our doubts of today.", "author": "Franklin D. Roosevelt"},
    {"text": "What lies behind us and what lies before us are tiny matters compared to what lies within us.", "author": "Ralph Waldo Emerson"},
    {"text": "Disciplining yourself to do what you know is right and important, although difficult, is the highroad to pride, self-esteem, and personal satisfaction.", "author": "Brian Tracy"},
    {"text": "You don't have to be great to start, but you have to start to be great.", "author": "Zig Ziglar"},
    {"text": "Do not wait; the time will never be 'just right.'", "author": "Napoleon Hill"},
    {"text": "The way to get started is to quit talking and begin doing.", "author": "Walt Disney"},
    {"text": "Setting goals is the first step in turning the invisible into the visible.", "author": "Tony Robbins"},
    {"text": "He who has a why to live can bear almost any how.", "author": "Friedrich Nietzsche"},
    {"text": "Courage doesn't always roar. Sometimes courage is the quiet voice at the end of the day saying, 'I will try again tomorrow.'", "author": "Mary Anne Radmacher"},
    {"text": "Fall seven times and stand up eight.", "author": "Japanese Proverb"},
    {"text": "Your life does not get better by chance, it gets better by change.", "author": "Jim Rohn"},
    {"text": "Success is the sum of small efforts, repeated day in and day out.", "author": "Robert Collier"},
    {"text": "Discipline is choosing between what you want now and what you want most.", "author": "Abraham Lincoln"},
    {"text": "Push yourself, because no one else is going to do it for you.", "author": "Anonymous"}
]

def get_random_quote(exclude_id: int = -1) -> Tuple[int, Dict[str, str]]:
    """Get a random quote, ensuring no consecutive repetition for the same user."""
    total_quotes = len(MOTIVATIONAL_QUOTES)
    if total_quotes <= 1:
        return 0, MOTIVATIONAL_QUOTES[0]

    chosen_id = random.randint(0, total_quotes - 1)
    while chosen_id == exclude_id:
        chosen_id = random.randint(0, total_quotes - 1)

    return chosen_id, MOTIVATIONAL_QUOTES[chosen_id]

def format_quote_message(quote: Dict[str, str], header: str = "✨ <b>Daily Motivation</b> ✨") -> str:
    """Format quote into HTML string."""
    return (
        f"{header}\n\n"
        f"<i>\"{quote['text']}\"</i>\n\n"
        f"✍️ <b>— {quote.get('author', 'Unknown')}</b>\n\n"
        f"🌟 <i>Have a productive and inspired day!</i>"
    )

WELCOME_TEXT = (
    "👋 <b>Welcome to Daily Motivation Bot!</b>\n\n"
    "I am here to keep you inspired, focused, and energized every day.\n\n"
    "<b>What I can do for you:</b>\n"
    "• Send you automated daily motivation at your preferred time\n"
    "• Deliver on-demand motivational quotes instantly\n"
    "• Custom delivery times and timezones suited to your location\n\n"
    "Use the menu below to get started!"
)

HELP_TEXT = (
    "ℹ️ <b>Daily Motivation Bot — Help Guide</b>\n\n"
    "<b>Available Commands:</b>\n"
    "• /start - Open the main menu\n"
    "• /motivate - Receive an instant quote\n"
    "• /daily - Enable/disable daily motivation\n"
    "• /settings - Customize time and timezone\n"
    "• /status - Check your subscription settings\n"
    "• /stop - Unsubscribe from daily updates\n"
    "• /about - Learn more about this bot\n"
    "• /help - Display this help message\n\n"
    "<i>Tip: You can use the inline buttons for quick navigation!</i>"
)

ABOUT_TEXT = (
    "🌟 <b>About Daily Motivation Bot</b>\n\n"
    "<b>Bot Handle:</b> @BirdPrekChakV99SBS24bot\n"
    "<b>Purpose:</b> Delivering curated positive thoughts and wisdom to brighten your day.\n"
    "<b>Version:</b> 1.0.0 (Production Ready)\n"
    "<b>Built with:</b> Python 3.11, python-telegram-bot, and APScheduler.\n\n"
    "<i>\"Small daily actions compound into extraordinary lives.\"</i>"
)
