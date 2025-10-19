"""
Script to create sample Excel files for testing the RAG system.
"""
import pandas as pd
from pathlib import Path

def create_sample_data():
    """Create sample data for testing."""

    # Sample data - Energy suppliers
    suppliers_renewable = [
        {
            "Denumire": "Eolica Energy SRL",
            "Tip Sursa": "Eoliană",
            "Putere Instalata": "150 MW",
            "Loc Racordare": "Stația Electrică Constanța Sud",
            "Adresa": "Constanța, România",
            "Persoana Contact": "Ion Popescu",
            "Telefon": "+40 744 123 456",
            "Email": "ion.popescu@eolicaenergy.ro"
        },
        {
            "Denumire": "Solar Power Romania",
            "Tip Sursa": "Fotovoltaică",
            "Putere Instalata": "80 MW",
            "Loc Racordare": "Stația Electrică Giurgiu",
            "Adresa": "Giurgiu, România",
            "Persoana Contact": "Maria Ionescu",
            "Telefon": "+40 755 987 654",
            "Email": "maria.ionescu@solarpower.ro"
        },
        {
            "Denumire": "Wind Solutions SRL",
            "Tip Sursa": "Eoliană",
            "Putere Instalata": "120 MW",
            "Loc Racordare": "Stația Electrică Tulcea",
            "Adresa": "Tulcea, Dobrogea, România",
            "Persoana Contact": "Andrei Marin",
            "Telefon": "+40 766 555 333",
            "Email": "andrei.marin@windsolutions.ro"
        },
        {
            "Denumire": "Hydro Power Carpathians",
            "Tip Sursa": "Hidroelectrică",
            "Putere Instalata": "250 MW",
            "Loc Racordare": "Stația Electrică Sibiu",
            "Adresa": "Sibiu, Transilvania, România",
            "Persoana Contact": "Elena Dumitrescu",
            "Telefon": "+40 744 222 111",
            "Email": "elena.d@hydropower.ro"
        },
        {
            "Denumire": "Green Energy Solutions",
            "Tip Sursa": "Fotovoltaică",
            "Putere Instalata": "45 MW",
            "Loc Racordare": "Stația Electrică Timișoara Est",
            "Adresa": "Timișoara, Banat, România",
            "Persoana Contact": "Gheorghe Popa",
            "Telefon": "+40 733 444 555",
            "Email": "gheorghe.popa@greenenergy.ro"
        }
    ]

    suppliers_conventional = [
        {
            "Denumire": "ThermoGen Energy",
            "Tip Sursa": "Hidrocarburi",
            "Putere Instalata": "400 MW",
            "Loc Racordare": "Stația Electrică București Sud",
            "Adresa": "București, Sector 4, România",
            "Persoana Contact": "Vasile Stoica",
            "Telefon": "+40 755 111 222",
            "Email": "vasile.stoica@thermogen.ro"
        },
        {
            "Denumire": "Nuclear Power Romania",
            "Tip Sursa": "Nucleară",
            "Putere Instalata": "1400 MW",
            "Loc Racordare": "Stația Electrică Cernavodă",
            "Adresa": "Cernavodă, Constanța, România",
            "Persoana Contact": "Mihai Constantinescu",
            "Telefon": "+40 744 888 999",
            "Email": "mihai.c@nuclearpower.ro"
        },
        {
            "Denumire": "BioEnergy Plant SRL",
            "Tip Sursa": "Biomasă",
            "Putere Instalata": "25 MW",
            "Loc Racordare": "Stația Electrică Bacău",
            "Adresa": "Bacău, Moldova, România",
            "Persoana Contact": "Ana Barbu",
            "Telefon": "+40 766 333 444",
            "Email": "ana.barbu@bioenergy.ro"
        }
    ]

    # Large consumers
    large_consumers = [
        {
            "Client": "ArcelorMittal Galați",
            "Consum Mediu": "350 MW",
            "Tip Client": "Industrial",
            "Adresa": "Galați, România",
            "Persoana Contact": "Dan Popescu",
            "Telefon": "+40 744 567 890",
            "Email": "dan.popescu@arcelormittal.ro"
        },
        {
            "Client": "Metro Cash & Carry România",
            "Consum Mediu": "15 MW",
            "Tip Client": "Comercial",
            "Adresa": "București, România",
            "Persoana Contact": "Cristina Moldovan",
            "Telefon": "+40 755 234 567",
            "Email": "cristina.moldovan@metro.ro"
        },
        {
            "Client": "Automobile Dacia Mioveni",
            "Consum Mediu": "80 MW",
            "Tip Client": "Industrial",
            "Adresa": "Mioveni, Argeș, România",
            "Persoana Contact": "Radu Ionescu",
            "Telefon": "+40 766 789 012",
            "Email": "radu.ionescu@dacia.ro"
        }
    ]

    return suppliers_renewable, suppliers_conventional, large_consumers


def create_excel_files():
    """Create sample Excel files."""

    # Create data directory
    data_dir = Path("data/input")
    data_dir.mkdir(parents=True, exist_ok=True)

    # Get sample data
    renewable, conventional, consumers = create_sample_data()

    # Create first Excel file - Renewable energy suppliers
    file1 = data_dir / "furnizori_energie_regenerabila.xlsx"
    with pd.ExcelWriter(file1, engine='openpyxl') as writer:
        df_renewable = pd.DataFrame(renewable)
        df_renewable.to_excel(writer, sheet_name='Energie Regenerabila', index=False)

    print(f"✓ Created: {file1}")

    # Create second Excel file - Conventional energy
    file2 = data_dir / "furnizori_energie_conventionala.xlsx"
    with pd.ExcelWriter(file2, engine='openpyxl') as writer:
        df_conventional = pd.DataFrame(conventional)
        df_conventional.to_excel(writer, sheet_name='Energie Conventionala', index=False)

    print(f"✓ Created: {file2}")

    # Create third Excel file - Large consumers
    file3 = data_dir / "consumatori_mari.xlsx"
    with pd.ExcelWriter(file3, engine='openpyxl') as writer:
        df_consumers = pd.DataFrame(consumers)
        df_consumers.to_excel(writer, sheet_name='Consumatori', index=False)

    print(f"✓ Created: {file3}")

    # Create combined file with multiple sheets
    file4 = data_dir / "date_complete_energie_2024.xlsx"
    with pd.ExcelWriter(file4, engine='openpyxl') as writer:
        df_renewable = pd.DataFrame(renewable)
        df_conventional = pd.DataFrame(conventional)
        df_consumers = pd.DataFrame(consumers)

        df_renewable.to_excel(writer, sheet_name='Furnizori Regenerabili', index=False)
        df_conventional.to_excel(writer, sheet_name='Furnizori Conventionali', index=False)
        df_consumers.to_excel(writer, sheet_name='Consumatori Mari', index=False)

    print(f"✓ Created: {file4}")

    print(f"\n✓ Successfully created {4} sample Excel files in {data_dir}")
    print("\nSample data includes:")
    print(f"  - {len(renewable)} renewable energy suppliers")
    print(f"  - {len(conventional)} conventional energy suppliers")
    print(f"  - {len(consumers)} large energy consumers")


if __name__ == "__main__":
    print("Creating sample Excel files for RAG system testing...\n")
    create_excel_files()
