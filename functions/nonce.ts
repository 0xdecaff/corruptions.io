import { Handler } from "@netlify/functions";

const handler: Handler = async (event, context) => {
  const nonce = (Math.random() + 1).toString(36).substring(4);
  return {
    statusCode: 200,
    body: nonce,
  };
};

export { handler };
