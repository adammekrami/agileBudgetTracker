import pytest
from decimal import Decimal
from django.test import TestCase
from app.models import Project, Sprint, SprintMetric
from app.serializers import SprintMetricSerializer
from datetime import date, timedelta


class TestROICalculations(TestCase):
    """
    Test suite for ROI calculations in SprintMetric model and serializer.
    """
    
    def setUp(self):
        """
        Set up test data that will be used across multiple tests.
        """
        # Create a test project
        self.project = Project.objects.create(
            name="Test Project",
            description="A project for testing ROI calculations"
        )
        
        # Create a test sprint
        self.sprint = Sprint.objects.create(
            project=self.project,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=14)
        )
    
    def test_roi_calculation_positive(self):
        """
        Test ROI calculation with positive return.
        Expected: (1500 - 1000) / 1000 = 0.5 (50% ROI)
        """
        metric = SprintMetric.objects.create(
            sprint=self.sprint,
            cost=Decimal('1000.00'),
            estimated_business_value=Decimal('1500.00'),
            velocity=20
        )
        
        # Test model property
        expected_roi = 0.5
        self.assertAlmostEqual(metric.roi, expected_roi, places=4)
        
        # Test serializer
        serializer = SprintMetricSerializer(metric)
        self.assertAlmostEqual(serializer.data['roi'], expected_roi, places=4)
    
    def test_roi_calculation_negative(self):
        """
        Test ROI calculation with negative return (loss).
        Expected: (500 - 1000) / 1000 = -0.5 (-50% ROI)
        """
        metric = SprintMetric.objects.create(
            sprint=self.sprint,
            cost=Decimal('1000.00'),
            estimated_business_value=Decimal('500.00'),
            velocity=15
        )
        
        expected_roi = -0.5
        self.assertAlmostEqual(metric.roi, expected_roi, places=4)
        
        # Test serializer
        serializer = SprintMetricSerializer(metric)
        self.assertAlmostEqual(serializer.data['roi'], expected_roi, places=4)
    
    def test_roi_zero_cost(self):
        """
        Test ROI calculation when cost is zero.
        Expected: None (to avoid division by zero)
        """
        metric = SprintMetric.objects.create(
            sprint=self.sprint,
            cost=Decimal('0.00'),
            estimated_business_value=Decimal('1000.00'),
            velocity=10
        )
        
        # Model property should return None
        self.assertIsNone(metric.roi)
        
        # Serializer should also return None
        serializer = SprintMetricSerializer(metric)
        self.assertIsNone(serializer.data['roi'])
    
    def test_roi_break_even(self):
        """
        Test ROI calculation at break-even point.
        Expected: (1000 - 1000) / 1000 = 0.0 (0% ROI)
        """
        metric = SprintMetric.objects.create(
            sprint=self.sprint,
            cost=Decimal('1000.00'),
            estimated_business_value=Decimal('1000.00'),
            velocity=18
        )
        
        expected_roi = 0.0
        self.assertEqual(metric.roi, expected_roi)
        
        # Test serializer
        serializer = SprintMetricSerializer(metric)
        self.assertEqual(serializer.data['roi'], expected_roi)
    
    def test_roi_high_return(self):
        """
        Test ROI calculation with very high return.
        Expected: (5000 - 1000) / 1000 = 4.0 (400% ROI)
        """
        metric = SprintMetric.objects.create(
            sprint=self.sprint,
            cost=Decimal('1000.00'),
            estimated_business_value=Decimal('5000.00'),
            velocity=25
        )
        
        expected_roi = 4.0
        self.assertAlmostEqual(metric.roi, expected_roi, places=4)
        
        # Test serializer
        serializer = SprintMetricSerializer(metric)
        self.assertAlmostEqual(serializer.data['roi'], expected_roi, places=4)
    
    def test_roi_with_decimals(self):
        """
        Test ROI calculation with decimal values.
        Expected: (1234.56 - 987.65) / 987.65 ≈ 0.2500
        """
        metric = SprintMetric.objects.create(
            sprint=self.sprint,
            cost=Decimal('987.65'),
            estimated_business_value=Decimal('1234.56'),
            velocity=22
        )
        
        expected_roi = (Decimal('1234.56') - Decimal('987.65')) / Decimal('987.65')
        self.assertAlmostEqual(metric.roi, float(expected_roi), places=4)
        
        # Test serializer
        serializer = SprintMetricSerializer(metric)
        self.assertAlmostEqual(serializer.data['roi'], float(expected_roi), places=4)


# Pytest-style tests (alternative approach)
@pytest.mark.django_db
class TestROICalculationsPytest:
    """
    Alternative test implementation using pytest syntax.
    """
    
    def test_roi_calculation(self):
        """Test basic ROI calculation."""
        project = Project.objects.create(name="Pytest Project")
        sprint = Sprint.objects.create(
            project=project,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=14)
        )
        metric = SprintMetric.objects.create(
            sprint=sprint,
            cost=Decimal('1000.00'),
            estimated_business_value=Decimal('1500.00'),
            velocity=20
        )
        
        assert metric.roi == 0.5
    
    def test_roi_zero_cost_pytest(self):
        """Test ROI calculation with zero cost."""
        project = Project.objects.create(name="Pytest Project Zero Cost")
        sprint = Sprint.objects.create(
            project=project,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=14)
        )
        metric = SprintMetric.objects.create(
            sprint=sprint,
            cost=Decimal('0.00'),
            estimated_business_value=Decimal('1000.00'),
            velocity=15
        )
        
        assert metric.roi is None
        
        # Verify serializer also handles it correctly
        serializer = SprintMetricSerializer(metric)
        assert serializer.data['roi'] is None
```

---

## **Additional Setup Instructions**

To complete the setup, you'll also need:

### **`backend/requirements.txt`**

Add these dependencies to your requirements.txt:
```
Django==4.2.7
djangorestframework==3.14.0
psycopg2-binary==2.9.9
drf-yasg==1.21.7
django-filter==23.5
django-cors-headers==4.3.1
pytest==7.4.3
pytest-django==4.7.0