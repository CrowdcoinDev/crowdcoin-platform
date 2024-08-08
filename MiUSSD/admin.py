from django.contrib import admin
from .models import Campaign, Node, NodeResponse, Interaction, NodeResponse

class NodeResponseInline(admin.TabularInline):
    model = NodeResponse
    extra = 1
    fk_name = 'node'

class NodeInline(admin.TabularInline):
    model = Node
    fk_name = 'campaign'
    extra = 1

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    inlines = [NodeInline]
    list_display = ['name', 'ussd_number', 'starting_node']
    fields = ['name', 'ussd_number', 'starting_node']

@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'campaign', 'text_response', 'link_response', 'function_response', 'script_response']
    fields = ['name', 'campaign', 'text_response', 'link_response', 'function_response', 'script_response']
    inlines = [NodeResponseInline]

@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ['user', 'node', 'response', 'timestamp']
    readonly_fields = ['session_data']

admin.site.register(NodeResponse)