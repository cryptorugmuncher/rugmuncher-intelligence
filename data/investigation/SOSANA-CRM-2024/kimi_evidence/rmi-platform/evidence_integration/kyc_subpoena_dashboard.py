#!/usr/bin/env python3
"""
KYC Subpoena Tracking Dashboard
Manages legal requests to exchanges for user identification
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class SubpoenaStatus(Enum):
    DRAFT = "draft"
    PENDING_LEGAL_REVIEW = "pending_legal_review"
    READY_FOR_SUBMISSION = "ready_for_submission"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    PROCESSING = "processing"
    RESPONDED = "responded"
    ENFORCED = "enforced"
    REJECTED = "rejected"
    APPEALED = "appealed"

class PriorityLevel(Enum):
    CRITICAL = "critical"  # Active threat, immediate action
    HIGH = "high"          # Significant funds, time-sensitive
    MEDIUM = "medium"      # Standard priority
    LOW = "low"            # Informational

@dataclass
class ExchangeContact:
    exchange: str
    legal_email: str
    compliance_portal: Optional[str]
    subpoena_address: Optional[str]
    response_time_days: int
    ml_required: bool
    notes: str

@dataclass
class SubpoenaDocument:
    id: str
    subpoena_id: str
    document_type: str  # "petition", "affidavit", "exhibit", "response", "supplement"
    filename: str
    file_url: str
    uploaded_by: str
    uploaded_at: datetime
    description: str

@dataclass
class SubpoenaTimeline:
    id: str
    subpoena_id: str
    event_type: str
    description: str
    timestamp: datetime
    performed_by: Optional[str]
    metadata: Dict

@dataclass
class KycSubpoena:
    id: str
    case_id: str
    exchange: str
    user_id: str
    wallet_addresses: List[str]
    estimated_funds: float
    priority: PriorityLevel
    legal_basis: str
    status: SubpoenaStatus
    
    # Request details
    requesting_agency: str
    requesting_agent: str
    agent_contact: str
    case_number: str
    
    # Timeline
    date_created: datetime
    date_submitted: Optional[datetime]
    date_acknowledged: Optional[datetime]
    date_response: Optional[datetime]
    date_enforced: Optional[datetime]
    
    # Response data
    response_data: Optional[Dict]
    user_identity: Optional[Dict]
    related_accounts: List[str]
    
    # Internal tracking
    assigned_attorney: Optional[str]
    notes: str
    tags: List[str]


class ExchangeRegistry:
    """Registry of exchange contact information and requirements"""
    
    EXCHANGES = {
        "Gate.io": ExchangeContact(
            exchange="Gate.io",
            legal_email="legal@gate.io",
            compliance_portal="https://gate.io/compliance",
            subpoena_address="Gate Technology Inc., Legal Department, Suite 100, George Town, Cayman Islands",
            response_time_days=30,
            ml_required=True,
            notes="Requires MLAT for non-US agencies. Responsive to well-documented requests."
        ),
        "Coinbase": ExchangeContact(
            exchange="Coinbase",
            legal_email="legal@coinbase.com",
            compliance_portal="https://coinbase.com/legal",
            subpoena_address="Coinbase, Inc., Attn: Legal Process, 100 Pine Street, Suite 1250, San Francisco, CA 94111",
            response_time_days=14,
            ml_required=False,
            notes="US-based, fast response. Requires 18 USC 2703(d) order for content."
        ),
        "Binance": ExchangeContact(
            exchange="Binance",
            legal_email="legal@binance.com",
            compliance_portal=None,
            subpoena_address="Binance Holdings Limited, Legal Department, PO Box 173, Kingston upon Thames, Surrey KT1 9HH, UK",
            response_time_days=45,
            ml_required=True,
            notes="Complex jurisdiction. May require multiple legal instruments."
        ),
        "Kraken": ExchangeContact(
            exchange="Kraken",
            legal_email="legal@kraken.com",
            compliance_portal="https://kraken.com/legal",
            subpoena_address="Payward Inc. dba Kraken, Attn: Legal Department, 237 Kearny Street #102, San Francisco, CA 94108",
            response_time_days=21,
            ml_required=False,
            notes="Cooperative with law enforcement. US-based operations."
        ),
        "KuCoin": ExchangeContact(
            exchange="KuCoin",
            legal_email="legal@kucoin.com",
            compliance_portal=None,
            subpoena_address="MEK Global Limited, Legal Department, Suite 603, 6/F Laws Commercial Plaza, 788 Cheung Sha Wan Road, Kowloon, Hong Kong",
            response_time_days=60,
            ml_required=True,
            notes="Hong Kong jurisdiction. Slow response times."
        )
    }
    
    @classmethod
    def get_exchange(cls, name: str) -> Optional[ExchangeContact]:
        return cls.EXCHANGES.get(name)
    
    @classmethod
    def get_all_exchanges(cls) -> List[ExchangeContact]:
        return list(cls.EXCHANGES.values())


class SubpoenaManager:
    """Manage KYC subpoena lifecycle"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.subpoenas: Dict[str, KycSubpoena] = {}
    
    def create_subpoena(
        self,
        case_id: str,
        exchange: str,
        user_id: str,
        wallet_addresses: List[str],
        estimated_funds: float,
        priority: PriorityLevel,
        legal_basis: str,
        requesting_agency: str,
        requesting_agent: str,
        agent_contact: str,
        case_number: str,
        assigned_attorney: Optional[str] = None,
        notes: str = ""
    ) -> KycSubpoena:
        """Create a new KYC subpoena"""
        
        subpoena_id = f"kyc_{exchange.lower()}_{datetime.now().strftime('%Y%m%d')}_{user_id[:8]}"
        
        subpoena = KycSubpoena(
            id=subpoena_id,
            case_id=case_id,
            exchange=exchange,
            user_id=user_id,
            wallet_addresses=wallet_addresses,
            estimated_funds=estimated_funds,
            priority=priority,
            legal_basis=legal_basis,
            status=SubpoenaStatus.DRAFT,
            requesting_agency=requesting_agency,
            requesting_agent=requesting_agent,
            agent_contact=agent_contact,
            case_number=case_number,
            date_created=datetime.now(),
            date_submitted=None,
            date_acknowledged=None,
            date_response=None,
            date_enforced=None,
            response_data=None,
            user_identity=None,
            related_accounts=[],
            assigned_attorney=assigned_attorney,
            notes=notes,
            tags=[]
        )
        
        self.subpoenas[subpoena_id] = subpoena
        return subpoena
    
    def transition_status(
        self, 
        subpoena_id: str, 
        new_status: SubpoenaStatus,
        performed_by: str,
        notes: str = ""
    ):
        """Transition subpoena to new status"""
        subpoena = self.subpoenas.get(subpoena_id)
        if not subpoena:
            raise ValueError(f"Subpoena {subpoena_id} not found")
        
        old_status = subpoena.status
        subpoena.status = new_status
        
        # Update timestamps based on status
        if new_status == SubpoenaStatus.SUBMITTED:
            subpoena.date_submitted = datetime.now()
        elif new_status == SubpoenaStatus.ACKNOWLEDGED:
            subpoena.date_acknowledged = datetime.now()
        elif new_status == SubpoenaStatus.RESPONDED:
            subpoena.date_response = datetime.now()
        elif new_status == SubpoenaStatus.ENFORCED:
            subpoena.date_enforced = datetime.now()
        
        # Add timeline entry
        self._add_timeline_entry(
            subpoena_id=subpoena_id,
            event_type="status_change",
            description=f"Status changed from {old_status.value} to {new_status.value}",
            performed_by=performed_by,
            metadata={"old_status": old_status.value, "new_status": new_status.value, "notes": notes}
        )
    
    def add_response_data(
        self,
        subpoena_id: str,
        response_data: Dict,
        user_identity: Dict,
        related_accounts: List[str]
    ):
        """Add exchange response data"""
        subpoena = self.subpoenas.get(subpoena_id)
        if not subpoena:
            raise ValueError(f"Subpoena {subpoena_id} not found")
        
        subpoena.response_data = response_data
        subpoena.user_identity = user_identity
        subpoena.related_accounts = related_accounts
        
        self.transition_status(subpoena_id, SubpoenaStatus.RESPONDED, "system", "Exchange response received")
    
    def _add_timeline_entry(
        self,
        subpoena_id: str,
        event_type: str,
        description: str,
        performed_by: Optional[str],
        metadata: Dict
    ):
        """Add timeline entry for subpoena"""
        entry = SubpoenaTimeline(
            id=f"tl_{datetime.now().strftime('%Y%m%d%H%M%S')}_{subpoena_id[:8]}",
            subpoena_id=subpoena_id,
            event_type=event_type,
            description=description,
            timestamp=datetime.now(),
            performed_by=performed_by,
            metadata=metadata
        )
        # Would save to Supabase
        return entry
    
    def get_subpoena_summary(self, subpoena_id: str) -> Dict:
        """Get summary of subpoena status"""
        subpoena = self.subpoenas.get(subpoena_id)
        if not subpoena:
            return None
        
        exchange = ExchangeRegistry.get_exchange(subpoena.exchange)
        
        # Calculate response deadline
        deadline = None
        if subpoena.date_submitted and exchange:
            deadline = subpoena.date_submitted + timedelta(days=exchange.response_time_days)
        
        # Calculate days remaining
        days_remaining = None
        if deadline:
            days_remaining = (deadline - datetime.now()).days
        
        return {
            "id": subpoena.id,
            "exchange": subpoena.exchange,
            "user_id": subpoena.user_id,
            "wallet_count": len(subpoena.wallet_addresses),
            "estimated_funds": subpoena.estimated_funds,
            "priority": subpoena.priority.value,
            "status": subpoena.status.value,
            "date_submitted": subpoena.date_submitted.isoformat() if subpoena.date_submitted else None,
            "response_deadline": deadline.isoformat() if deadline else None,
            "days_remaining": days_remaining,
            "has_response": subpoena.response_data is not None,
            "user_identified": subpoena.user_identity is not None,
            "assigned_attorney": subpoena.assigned_attorney,
            "exchange_contact": asdict(exchange) if exchange else None
        }
    
    def get_all_summaries(self) -> List[Dict]:
        """Get summaries of all subpoenas"""
        return [self.get_subpoena_summary(sid) for sid in self.subpoenas.keys()]
    
    def get_statistics(self) -> Dict:
        """Get subpoena statistics"""
        subpoenas = list(self.subpoenas.values())
        
        return {
            "total_subpoenas": len(subpoenas),
            "by_status": {
                status.value: len([s for s in subpoenas if s.status == status])
                for status in SubpoenaStatus
            },
            "by_priority": {
                priority.value: len([s for s in subpoenas if s.priority == priority])
                for priority in PriorityLevel
            },
            "by_exchange": self._group_by_exchange(subpoenas),
            "total_funds_traced": sum(s.estimated_funds for s in subpoenas),
            "identified_users": len([s for s in subpoenas if s.user_identity]),
            "pending_response": len([s for s in subpoenas if s.status in [
                SubpoenaStatus.SUBMITTED, SubpoenaStatus.ACKNOWLEDGED, SubpoenaStatus.PROCESSING
            ]]),
            "overdue": len([s for s in subpoenas if self._is_overdue(s)])
        }
    
    def _group_by_exchange(self, subpoenas: List[KycSubpoena]) -> Dict:
        """Group subpoenas by exchange"""
        result = {}
        for s in subpoenas:
            result[s.exchange] = result.get(s.exchange, 0) + 1
        return result
    
    def _is_overdue(self, subpoena: KycSubpoena) -> bool:
        """Check if subpoena response is overdue"""
        if not subpoena.date_submitted:
            return False
        
        exchange = ExchangeRegistry.get_exchange(subpoena.exchange)
        if not exchange:
            return False
        
        deadline = subpoena.date_submitted + timedelta(days=exchange.response_time_days)
        return datetime.now() > deadline and subpoena.status not in [
            SubpoenaStatus.RESPONDED, SubpoenaStatus.ENFORCED
        ]
    
    def generate_subpoena_template(self, subpoena_id: str) -> str:
        """Generate legal subpoena document template"""
        subpoena = self.subpoenas.get(subpoena_id)
        if not subpoena:
            return ""
        
        exchange = ExchangeRegistry.get_exchange(subpoena.exchange)
        
        template = f'''
IN THE [COURT NAME]
[CASE NUMBER]

SUBPOENA DUCES TECUM

TO: {subpoena.exchange}
    {exchange.subpoena_address if exchange else "[Address Required]"}

RE: {subpoena.case_number}
    {subpoena.requesting_agency}

YOU ARE HEREBY COMMANDED to produce the following documents and information:

1. USER ACCOUNT INFORMATION
   User ID: {subpoena.user_id}
   
   a. Complete account registration information including:
      - Full legal name
      - Date of birth
      - Physical address
      - Email address(es)
      - Phone number(s)
      - Government-issued identification documents
      - Selfie verification images
      - IP address logs
      - Device fingerprints

2. TRANSACTION HISTORY
   For the following wallet addresses:
   {chr(10).join("   - " + addr for addr in subpoena.wallet_addresses)}
   
   a. All cryptocurrency deposits and withdrawals
   b. All trading activity
   c. All fiat currency transactions
   d. Timestamp and IP address for each transaction

3. FINANCIAL INFORMATION
   a. All bank account information linked to the account
   b. All payment method details
   c. Account balance history

LEGAL BASIS: {subpoena.legal_basis}

ESTIMATED FUNDS INVOLVED: ${subpoena.estimated_funds:,.2f}

This subpoena is issued in connection with an ongoing criminal investigation 
into cryptocurrency fraud and money laundering.

Date: {datetime.now().strftime("%B %d, %Y")}

_________________________
{subpoena.requesting_agent}
{subpoena.requesting_agency}
{subpoena.agent_contact}
'''
        return template


class SubpoenaDashboard:
    """Generate HTML dashboard for KYC subpoena tracking"""
    
    def __init__(self, manager: SubpoenaManager):
        self.manager = manager
    
    def generate_dashboard(self) -> str:
        """Generate complete HTML dashboard"""
        stats = self.manager.get_statistics()
        summaries = self.manager.get_all_summaries()
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KYC Subpoena Tracking Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }}
        
        .header {{
            background: rgba(0, 0, 0, 0.7);
            padding: 30px;
            border-bottom: 3px solid #9900ff;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            background: linear-gradient(90deg, #9900ff, #ff00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid #333;
            transition: all 0.3s;
        }}
        
        .stat-card:hover {{
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-5px);
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #9900ff;
        }}
        
        .stat-label {{
            color: #888;
            margin-top: 10px;
            text-transform: uppercase;
            font-size: 0.9em;
        }}
        
        .section {{
            padding: 30px;
        }}
        
        .section h2 {{
            color: #9900ff;
            margin-bottom: 20px;
            font-size: 1.5em;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 10px;
            overflow: hidden;
        }}
        
        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #333;
        }}
        
        th {{
            background: rgba(153, 0, 255, 0.2);
            color: #9900ff;
            text-transform: uppercase;
            font-size: 0.85em;
        }}
        
        tr:hover {{
            background: rgba(255, 255, 255, 0.05);
        }}
        
        .status-badge {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        
        .status-draft {{ background: #666; }}
        .status-submitted {{ background: #0066ff; }}
        .status-acknowledged {{ background: #ffcc00; color: #000; }}
        .status-processing {{ background: #ff6600; }}
        .status-responded {{ background: #00ff00; color: #000; }}
        .status-enforced {{ background: #00cc00; color: #000; }}
        .status-rejected {{ background: #ff0000; }}
        
        .priority-critical {{ color: #ff0000; font-weight: bold; }}
        .priority-high {{ color: #ff6600; font-weight: bold; }}
        .priority-medium {{ color: #ffcc00; }}
        .priority-low {{ color: #00ff00; }}
        
        .overdue {{
            animation: pulse-red 2s infinite;
        }}
        
        @keyframes pulse-red {{
            0%, 100% {{ background: rgba(255, 0, 0, 0.1); }}
            50% {{ background: rgba(255, 0, 0, 0.3); }}
        }}
        
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #333;
            border-radius: 4px;
            overflow: hidden;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #9900ff, #ff00ff);
            transition: width 0.3s;
        }}
        
        .btn {{
            background: linear-gradient(90deg, #9900ff, #ff00ff);
            border: none;
            color: #fff;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.85em;
            transition: all 0.2s;
        }}
        
        .btn:hover {{
            transform: scale(1.05);
            box-shadow: 0 0 15px rgba(153, 0, 255, 0.5);
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 KYC Subpoena Tracking Dashboard</h1>
        <p style="color: #888; margin-top: 10px;">CRM Token Fraud Investigation</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{stats['total_subpoenas']}</div>
            <div class="stat-label">Total Subpoenas</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats['total_funds_traced']:,.0f}</div>
            <div class="stat-label">Total Funds Traced</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['identified_users']}</div>
            <div class="stat-label">Users Identified</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['pending_response']}</div>
            <div class="stat-label">Pending Response</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" style="color: {'#ff0000' if stats['overdue'] > 0 else '#00ff00'}">{stats['overdue']}</div>
            <div class="stat-label">Overdue</div>
        </div>
    </div>
    
    <div class="section">
        <h2>📋 Active Subpoenas</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Exchange</th>
                    <th>User ID</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Est. Funds</th>
                    <th>Submitted</th>
                    <th>Days Left</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>'''
        
        for summary in summaries:
            if not summary:
                continue
                
            days_left = summary.get('days_remaining', 'N/A')
            overdue_class = 'overdue' if days_left and isinstance(days_left, int) and days_left < 0 else ''
            
            html += f'''
                <tr class="{overdue_class}">
                    <td>{summary['id'][:20]}...</td>
                    <td>{summary['exchange']}</td>
                    <td><code>{summary['user_id'][:15]}...</code></td>
                    <td class="priority-{summary['priority']}">{summary['priority'].upper()}</td>
                    <td><span class="status-badge status-{summary['status']}">{summary['status']}</span></td>
                    <td>${summary['estimated_funds']:,.0f}</td>
                    <td>{summary['date_submitted'][:10] if summary['date_submitted'] else 'Not submitted'}</td>
                    <td>{days_left if isinstance(days_left, str) else f'{days_left} days'}</td>
                    <td><button class="btn">View</button></td>
                </tr>'''
        
        html += '''
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <h2>📊 Status Breakdown</h2>
        <table>
            <thead>
                <tr>
                    <th>Status</th>
                    <th>Count</th>
                    <th>Progress</th>
                </tr>
            </thead>
            <tbody>'''
        
        for status, count in stats['by_status'].items():
            if count > 0:
                percentage = (count / stats['total_subpoenas']) * 100
                html += f'''
                <tr>
                    <td>{status.replace('_', ' ').title()}</td>
                    <td>{count}</td>
                    <td>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {percentage}%"></div>
                        </div>
                    </td>
                </tr>'''
        
        html += '''
            </tbody>
        </table>
    </div>
</body>
</html>'''
        
        return html
    
    def export_dashboard(self, filepath: str = "kyc_dashboard.html"):
        """Export dashboard to HTML file"""
        html = self.generate_dashboard()
        with open(filepath, 'w') as f:
            f.write(html)
        return filepath


if __name__ == "__main__":
    # Demo usage
    manager = SubpoenaManager("https://example.supabase.co", "api_key")
    
    # Create sample subpoenas
    manager.create_subpoena(
        case_id="crm-token-fraud-2024",
        exchange="Gate.io",
        user_id="GATE_USER_8847291",
        wallet_addresses=["0xEXIT...GATE01"],
        estimated_funds=320000,
        priority=PriorityLevel.CRITICAL,
        legal_basis="18 USC 2703(d) - Stored Communications Act",
        requesting_agency="FBI Cyber Division",
        requesting_agent="Special Agent Smith",
        agent_contact="smith@fbi.gov",
        case_number="FBI-2024-CRM-001",
        assigned_attorney="Jane Doe, Esq.",
        notes="Primary exit vector. Identity will expose Tier 1 controller."
    )
    
    manager.create_subpoena(
        case_id="crm-token-fraud-2024",
        exchange="Coinbase",
        user_id="CB_USER_5521847",
        wallet_addresses=["0xEXIT...COIN01"],
        estimated_funds=185000,
        priority=PriorityLevel.CRITICAL,
        legal_basis="18 USC 2703(d) - Stored Communications Act",
        requesting_agency="FBI Cyber Division",
        requesting_agent="Special Agent Smith",
        agent_contact="smith@fbi.gov",
        case_number="FBI-2024-CRM-001",
        notes="Secondary exit. US-based = faster response."
    )
    
    # Generate dashboard
    dashboard = SubpoenaDashboard(manager)
    dashboard.export_dashboard("kyc_subpoena_dashboard.html")
    print("Dashboard exported to kyc_subpoena_dashboard.html")
    
    # Print statistics
    print("\nSubpoena Statistics:")
    print(json.dumps(manager.get_statistics(), indent=2))
