from django.core.management.base import BaseCommand
from user.models import FeedStock

class Command(BaseCommand):
    help = 'Check feed stock data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Checking feed stocks...")
        
        feed_types = {
            'starter': 'Starter Feed',
            'grower': 'Grower Feed',
            'finisher': 'Finisher Feed'
        }
        
        for feed_type, display_name in feed_types.items():
            stocks = FeedStock.objects.filter(feed_type=feed_type)
            self.stdout.write(f"\n{display_name}:")
            for stock in stocks:
                self.stdout.write(
                    f"- {stock.number_of_sacks} sacks at ₹{stock.price_per_sack} each"
                ) 