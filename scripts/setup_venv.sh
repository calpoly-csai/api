#!/bin/bash
python3.6 -m venv venv

echo "Then run the following in your shell:"
echo "\`\`\`"
echo "source venv/bin/activate"
echo "\`\`\`"
echo "*******************************"
echo "(Optional) To exit the venv shell type"
echo "\`\`\`"
echo "deactivate"
echo "\`\`\`"
echo "*******************************"
echo "Finally run the following (and do NOT upgrade pip because neuralcoref)"
echo "\`\`\`"
echo "pip3.6 install -r requirements.txt"
echo "\`\`\`"
echo "you can also just run ./scripts/install_reqs.sh"
