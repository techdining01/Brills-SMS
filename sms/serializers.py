# # sms/serializers.py
# from rest_framework import serializers
# import random

# class QuestionSerializer(serializers.ModelSerializer):
#     # This field holds the randomized options for the student
#     randomized_options = serializers.SerializerMethodField()

#     class Meta:
#         model = CBTQuestion
#         fields = ['id', 'question_text', 'randomized_options']

#     def get_randomized_options(self, obj: CBTQuestion):
#         """
#         Retrieves the options for the question and randomizes their order
#         based on the map stored in the current CBTExamSession.
#         """
#         # Get the context passed from the view (which must include the session data)
#         session_data = self.context.get('session_data')
#         if not session_data:
#             return []

#         # 1. Get the session data for this specific question ID
#         question_data = next((q for q in session_data['questions'] if q['question_id'] == obj.id), None)
#         if not question_data:
#             return []

#         # 2. Get the original options list (using attribute names)
#         original_options = [obj.option_a, obj.option_b, obj.option_c, obj.option_d]
        
#         # 3. Apply the randomized map (e.g., [3, 1, 0, 2])
#         # This creates the list of options in the order the student should see them.
#         randomized_options = [original_options[i] for i in question_data['option_map']]
        
#         # Return the options indexed 0, 1, 2, 3 as they appear on the screen
#         return list(enumerate(randomized_options))