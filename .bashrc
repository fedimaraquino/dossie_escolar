# Ativação automática do ambiente virtual
if [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
    echo "Ambiente virtual ativado automaticamente!"
fi
