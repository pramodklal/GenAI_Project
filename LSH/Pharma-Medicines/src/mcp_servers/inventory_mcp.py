"""
Inventory MCP Server - v1.0.0

MCP server for inventory management, supply chain operations, and material tracking.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any
import logging

from mcp_servers.base_mcp_server import MCPServerBase
from database.astra_helper import get_db_helper
from agents.supply_chain_agent import SupplyChainAgent

logger = logging.getLogger(__name__)


class InventoryMCPServer(MCPServerBase):
    """MCP Server for inventory and supply chain operations."""
    
    def __init__(self):
        super().__init__("Inventory MCP Server", "1.0.0")
        self.db = get_db_helper()
        self.supply_chain_agent = SupplyChainAgent()
    
    def _register_endpoints(self):
        """Register all inventory-related endpoints."""
        
        self.register_endpoint(
            name="get_material_inventory",
            handler=self._get_material_inventory,
            required_params=["material_id"],
            description="Get current inventory status for a material"
        )
        
        self.register_endpoint(
            name="check_low_stock_items",
            handler=self._check_low_stock_items,
            required_params=["threshold"],
            description="Get list of materials below reorder threshold"
        )
        
        self.register_endpoint(
            name="create_purchase_order",
            handler=self._create_purchase_order,
            required_params=["po_data"],
            description="Create a new purchase order for materials"
        )
        
        self.register_endpoint(
            name="update_material_quantity",
            handler=self._update_material_quantity,
            required_params=["material_id", "quantity", "transaction_type"],
            description="Update material quantity (receipt or consumption)"
        )
        
        self.register_endpoint(
            name="get_expiring_materials",
            handler=self._get_expiring_materials,
            required_params=["days_ahead"],
            description="Get materials expiring within specified period"
        )
        
        self.register_endpoint(
            name="forecast_material_demand",
            handler=self._forecast_material_demand,
            required_params=["material_id", "forecast_days"],
            description="AI-powered demand forecasting for material planning"
        )
    
    def _get_material_inventory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get material inventory status."""
        try:
            material_id = params["material_id"]
            
            material = self.db.get_material(material_id)
            if not material:
                return {
                    "status": "not_found",
                    "message": f"Material {material_id} not found"
                }
            
            # Get reorder recommendation
            reorder_calc = self.supply_chain_agent.calculate_reorder_points(material_id)
            
            return {
                "status": "success",
                "material": material,
                "reorder_analysis": reorder_calc
            }
            
        except Exception as e:
            logger.error(f"Error getting material inventory: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _check_low_stock_items(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check low stock items."""
        try:
            threshold = params.get("threshold", 1000)
            
            low_stock = self.db.get_low_stock_materials(threshold)
            
            # Analyze each material
            critical_items = []
            for material in low_stock:
                forecast = self.supply_chain_agent.forecast_demand(
                    material.get("material_id"),
                    forecast_days=30
                )
                
                if forecast.get("urgency") in ["critical", "high"]:
                    critical_items.append({
                        "material": material,
                        "forecast": forecast
                    })
            
            return {
                "status": "success",
                "total_low_stock": len(low_stock),
                "critical_items": len(critical_items),
                "low_stock_materials": low_stock,
                "critical_analysis": critical_items
            }
            
        except Exception as e:
            logger.error(f"Error checking low stock items: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _create_purchase_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create purchase order."""
        try:
            po_data = params["po_data"]
            
            # Validate required fields
            required_fields = ["po_id", "supplier_id", "items"]
            for field in required_fields:
                if field not in po_data:
                    return {
                        "status": "error",
                        "error": f"Missing required field: {field}"
                    }
            
            # Get supplier info
            supplier = self.db.get_supplier(po_data["supplier_id"])
            if not supplier:
                return {
                    "status": "error",
                    "error": "Supplier not found"
                }
            
            # Analyze supplier performance
            supplier_analysis = self.supply_chain_agent.analyze_supplier_performance(
                po_data["supplier_id"]
            )
            
            # Create PO
            result = self.db.create_purchase_order(po_data)
            
            return {
                "status": "success",
                "message": "Purchase order created successfully",
                "po_id": po_data["po_id"],
                "supplier": supplier.get("name"),
                "supplier_rating": supplier_analysis.get("rating"),
                "estimated_delivery": f"{supplier_analysis.get('metrics', {}).get('lead_time_avg_days', 14)} days"
            }
            
        except Exception as e:
            logger.error(f"Error creating purchase order: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _update_material_quantity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update material quantity."""
        try:
            material_id = params["material_id"]
            quantity = params["quantity"]
            transaction_type = params["transaction_type"]
            
            # Validate transaction type
            valid_types = ["receipt", "consumption", "adjustment"]
            if transaction_type not in valid_types:
                return {
                    "status": "error",
                    "error": f"Invalid transaction type. Must be one of: {', '.join(valid_types)}"
                }
            
            result = self.db.update_material_quantity(
                material_id=material_id,
                quantity=quantity,
                transaction_type=transaction_type
            )
            
            # Get updated inventory status
            material = self.db.get_material(material_id)
            
            return {
                "status": "success",
                "message": f"Material quantity updated ({transaction_type})",
                "material_id": material_id,
                "new_quantity": material.get("quantity_in_stock") if material else None
            }
            
        except Exception as e:
            logger.error(f"Error updating material quantity: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _get_expiring_materials(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get expiring materials."""
        try:
            days_ahead = params.get("days_ahead", 30)
            
            # Use Supply Chain Agent
            report = self.supply_chain_agent.get_expiring_materials(days_ahead)
            
            return {
                "status": "success",
                "expiring_materials_report": report
            }
            
        except Exception as e:
            logger.error(f"Error getting expiring materials: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _forecast_material_demand(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Forecast material demand using AI."""
        try:
            material_id = params["material_id"]
            forecast_days = params.get("forecast_days", 30)
            
            # Use Supply Chain Agent
            forecast = self.supply_chain_agent.forecast_demand(material_id, forecast_days)
            
            # Get reorder recommendations
            reorder_calc = self.supply_chain_agent.calculate_reorder_points(material_id)
            
            return {
                "status": "success",
                "demand_forecast": forecast,
                "reorder_recommendations": reorder_calc
            }
            
        except Exception as e:
            logger.error(f"Error forecasting material demand: {str(e)}")
            return {"status": "error", "error": str(e)}


# Server initialization
def create_server():
    """Create and return Inventory MCP Server instance."""
    return InventoryMCPServer()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    server = create_server()
    print(f"✅ {server.server_name} v{server.version} initialized")
    print(f"📋 Registered {len(server.list_endpoints())} endpoints")
    
    # Display endpoints
    for endpoint in server.list_endpoints():
        print(f"  - {endpoint['name']}: {endpoint['description']}")
