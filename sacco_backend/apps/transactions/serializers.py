from decimal import Decimal
from rest_framework import serializers

from apps.transactions.models import Transaction, TransactionFee, TransactionLimit


class TransactionSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['transaction_ref', 'status', 'processed_date', 'created_at', 'updated_at']


class TransactionFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionFee
        fields = '__all__'


class TransactionLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionLimit
        fields = '__all__'


class TransferSerializer(serializers.Serializer):
    source_member_id = serializers.IntegerField()
    destination_member_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
    description = serializers.CharField(max_length=255, required=False)
    payment_method = serializers.ChoiceField(
        choices=['CASH', 'MOBILE_MONEY', 'BANK_TRANSFER', 'INTERNAL'], 
        default='INTERNAL'
    )


class TransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'member', 'transaction_type', 'amount', 'payment_method', 
            'source_account', 'destination_account', 'external_reference', 
            'description'
        ]
        
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value