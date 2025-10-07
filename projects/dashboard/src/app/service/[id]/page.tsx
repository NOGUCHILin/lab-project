import { notFound } from 'next/navigation';
import { SERVICES, getServiceById } from '@/config/services';
import { ServicePage } from '@/components/services/ServicePage';

interface ServiceDetailPageProps {
  params: {
    id: string;
  };
}

export async function generateStaticParams() {
  return SERVICES.map((service) => ({
    id: service.id,
  }));
}

export async function generateMetadata({ params }: ServiceDetailPageProps) {
  const { id } = await params;
  const service = getServiceById(id);

  if (!service) {
    return {
      title: 'Service Not Found',
    };
  }

  return {
    title: `${service.name} - Dashboard`,
    description: service.description,
  };
}

export default async function ServiceDetailPage({ params }: ServiceDetailPageProps) {
  const { id } = await params;
  const service = getServiceById(id);

  if (!service) {
    notFound();
  }

  return <ServicePage service={service} />;
}